## main

from sys import argv


# if you type python beeDataAcq setup, it will run the setup module, otherwise
# it will go straight to recording

if argv[-1] == "setup":
    import cameraSetup
    cameraSetup.main()

else:
    import saveVid
    saveVid.main()