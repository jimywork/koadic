# Koadic
Koadic, or COM Command & Control, is a Windows post-exploitation rootkit similar to other penetration testing tools such as Meterpreter and Powershell Empire. The major difference is that Koadic does most of its operations using Windows Script Host (a.k.a. JScript/VBScript), with compatibility in the core to support a default installation of Windows 2000 with no service packs (and potentially even versions of NT4) all the way through Windows 10.

It is possible to serve payloads completely in memory from stage 0 to beyond, as well as use cryptographically secure communications over SSL and TLS (depending on what the victim OS has enabled).

Koadic also attempts to be compatible with both Python 2 and Python 3.

### Demo

[![Koadic Demo](http://img.youtube.com/vi/hLdXp2WPvTs/0.jpg)](http://www.youtube.com/watch?v=hLdXp2WPvTs "Koadic Demo")

1. Hooks a zombie
2. Elevates integrity (UAC Bypass)
3. Dumps SAM/SECURITY hive for passwords
4. Scans local network for open SMB
5. Pivots to another machine

### Stagers
Stagers hook target zombies and allow you to use implants.

Module | Description
--------|------------
stager/js/mshta | serves payloads in memory using MSHTA.exe HTML Applications
stager/js/regsvr | serves payloads in memory using regsvr32.exe COM+ scriptlets
stager/js/rundll32_js | serves payloads in memory using rundll32.exe
stager/js/disk | serves payloads using files on disk

### Implants
Implants start jobs on zombies.

Module | Description
--------|------------
implant/elevate/bypassuac_eventvwr | Uses enigma0x3's eventvwr.exe exploit to bypass UAC on Windows 7, 8, and 10.
implant/elevate/bypassuac_sdclt | Uses enigma0x3's sdclt.exe exploit to bypass UAC on Windows 10.
implant/fun/thunderstruck | Maxes volume and opens a URL in a hidden window (AC/DC YouTube).
implant/fun/voice | Plays a message over text-to-speech.
implant/gather/clipboard | Retrieves the current content of the user clipboard.
implant/gather/hashdump_sam | Retrieves hashed passwords from the SAM hive.
implant/gather/hashdump_dc | Domain controller hashes from the NTDS.dit file.
implant/inject/reflectdll_excel | Injects a reflective-loaded DLL (if Excel is installed).
implant/inject/shellcode_excel | Runs arbitrary shellcode payload (if Excel is installed).
implant/manage/enable_rdesktop | Enables remote desktop on the target.
implant/manage/exec_cmd | Run an arbitrary command on the target, and optionally receive the output.
implant/manage/killav | iterate known antivirus processes, and attempt to end their execution.
implant/pivot/exec_wmi | Run a command on another machine using WMI.
implant/pivot/exec_psexec | Run a command on another machine using psexec.
implant/scan/tcp | Uses HTTP to scan open TCP ports on the target zombie LAN.
implant/utils/download_file | Downloads a file from the target zombie.
implant/utils/upload_file | Uploads a file from the listening server to the target zombies.

### Acknowledgements
Special thanks to research done by the following individuals:

- [@subTee](https://twitter.com/subTee)
- [@enigma0x3](https://twitter.com/enigma0x3)
- [@tiraniddo](https://twitter.com/tiraniddo)
- [@harmj0y](https://twitter.com/harmj0y)
- [@gentilkiwi](https://twitter.com/gentilkiwi)
- [@mattifestation](https://twitter.com/mattifestation)
- clymb3r
- [@Aleph_\__Naught](https://twitter.com/Aleph___Naught)
- [@The_Naterz](https://twitter.com/The_Naterz)
- [@JennaMagius](https://twitter.com/JennaMagius)
- [@zerosum0x0](https://twitter.com/zerosum0x0)
