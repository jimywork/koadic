try
{
    var output = Koadic.shell.exec("~CMD~", "~DIRECTORY~\\~FILE~.txt");
    Koadic.work.report(output);
}
catch (e)
{
    Koadic.work.error(e)
}

Koadic.exit();
