try
{
  var voiceObj = new ActiveXObject("sapi.spvoice");

  for (var i = 0; i < 50; ++i)
  {

      Koadic.WS.SendKeys(String.fromCharCode(0xAF));
  }

  voiceObj.Speak('wuh bruh');


  alert("YUH BRUH")
  Koadic.work.report("");
}
catch (e)
{
  Koadic.work.error(e)
}

  Koadic.exit();
