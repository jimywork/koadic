try
{
    var data = Koadic.file.readBinary("~RFILE~");

    data = data.replace(/\\/g, "\\\\");
    data = data.replace(/\0/g, "\\0")

    Koadic.work.report(data);
}
catch (e)
{
    Koadic.work.error(e);
}

Koadic.exit();
