from fabric.api import local, prefix
import os
import logging
import glob

log = logging.getLogger(__name__)


SIV_REFERENCE_REPO = "/mnt/secondary-siv/references"
SIV_MOVIE_ROOT = "/mnt/secondary-siv/testdata/LIMS"


def convert_reference(to_ds_exe, reference_info_xml, dataset_xml):
    return local("{e} {r} {d} ".format(e=to_ds_exe, r=reference_info_xml, d=dataset_xml))


def convert_references(to_ds_exe, reference_info_xmls, to_output_ds_func):
    """
    :param to_ds_exe: base reference info to dataset exe
    :param reference_info_xmls: list of abspaths to reference.info XML
    :param to_output_ds_func: Func(abs_ds_path) -> path of output dataset XML
    """
    for reference_info_xml in reference_info_xmls:
        try:
            output_xml = to_output_ds_func(reference_info_xml)
            s = os.path.getsize(reference_info_xml) / 1024.0 / 1024.0
            # just use the output file name
            name = os.path.basename(output_xml)
            if s < 1.0:
                log.info("Converting {n} -> {r}".format(n=name, r=reference_info_xml))
                convert_reference(to_ds_exe, reference_info_xml, output_xml)
            else:
                log.error("Reference TOO big to convert. {s:.2f} MB".format(s=s))
        except Exception as e:
            print "Unable to convert {r}. Error {e}".format(r=reference_info_xml, e=e)
            raise


def convert_references_repository(to_ds_cmd, reference_dir_name, to_output_ds_func):
    reference_info_xmls = (os.path.abspath(p) for p in glob.glob("{r}/*/reference.info.xml".format(r=reference_dir_name)))
    convert_references(to_ds_cmd, reference_info_xmls, to_output_ds_func)


def _to_output_dir_ds_func(output_dir):
    def to_ds_output(path):
        ds_basename = os.path.basename(path)
        return os.path.join(output_dir, ds_basename)
    return to_ds_output


def to_output_ds(ext, new_ext):
    def _to_output(path):
        if path.endswith(ext):
            return path.replace(ext, new_ext)
        raise ValueError("Unable to find {e} in {p}".format(e=ext, p=path))
    return _to_output


def default_convert_references_repo():
    """Simple conversion that assumes the exe is in the path"""
    to_ds_exe = "reference-to-dataset"

    # write to over the files named "reference.dataset.xml"
    # writer_func = to_output_ds("reference.info.xml", "reference.dataset.xml")

    # write a single output dir
    writer_func = _to_output_dir_ds_func(os.getcwd())
    return convert_references_repository(to_ds_exe, SIV_REFERENCE_REPO, writer_func)


def get_movie_metadata_xml(root_dir):
    def is_movie(f):
        return f.endswith(".metadata.xml")
    for root, dir_names, file_names in os.walk(root_dir):
        for file_name in file_names:
            if is_movie(file_name):
                yield os.path.join(root, file_name)


def convert_rs_movie(exe_path, rs_movie, output_dir):
    out_name = rs_movie.replace(".metadata.xml", ".hdfsubread.datset.xml")
    name = os.path.basename(out_name)
    out = os.path.join(output_dir, name)
    log.info("Converting {i} to {o}".format(i=rs_movie, o=out))
    return local("{e} {i} {o}".format(e=exe_path, i=rs_movie, o=out))


def convert_rs_movies(exe_path, rs_movies, output_dir):
    return [convert_rs_movie(exe_path, item, output_dir) for item in rs_movies]


def convert_all_rs_movies(exe_path, root_dir, output_dir):
    it = get_movie_metadata_xml(root_dir)
    return convert_rs_movies(exe_path, it, output_dir)

XSLT_CMD = "java -jar /home/UNIXHOME/mkocher/saxon-9.1.0.8.jar -xsl:/home/UNIXHOME/mkocher/HdfSubreads.xslt "


def to_xslt_cmd(movie_metadata, output_hdfsubread_xml):
    return "{e} -s:{i} -o:{o}".format(e=XSLT_CMD, i=movie_metadata, o=output_hdfsubread_xml)


def convert_all_rs_movies_xslt(root_dir, output_dir):
    for movie_file_name in get_movie_metadata_xml(root_dir):
        base_name = os.path.basename(movie_file_name)
        name = base_name.replace(".metadata.xml", ".hdfsubread2.dataset.xml")
        output_name = os.path.join(output_dir, name)
        cmd = to_xslt_cmd(movie_file_name, output_name)
        local(cmd)