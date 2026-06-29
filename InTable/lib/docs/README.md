# I-Table #

A Brute-Force bypass for 1upArcade Infinity Game Tables for access to standard Android Firmware

## Required ##

- 2.4G WiFi Network or HotSpot (5G Not Supported) |or| USB3.0 USB-A Male to USB-A Male Thunderbolt Transfer Cable
- PC |or| Android Device
- Latest ADB Binaries
- Latest Termux-App, Termux-Api, and Termux-Boot APK files
- Ungodly Ammounts of ***P A T I E N C E***

---

## Loops: Repetative Action Loops ##

```ini
[Reboot]
    To properly reboot, simply Hold the power button for ~3-5s and in the Middle-Right of the screen a small pop-up will appear with `Restart` and `Poweroff`.
    Use either one to shutdown the device, Restart just automatically turns it back on.
    Do NOT just unplug the Table at any point as a way to reboot!

[Comma Trick]
    ONLY works with the Stock OEM Android Keyboard, and this is patched in ALL I-Table Updates. This is why we MUST factory reset and not connect to wifi
    But simply trigger the Virtual Keyboard by pressing any text field. `Comma` should be just left of the space-bar but sometimes it gets hidden with other symbols in the `?123` tab, also located in the bottom-left.
    On the next tab you should see the comma now. Now simply hold the comma until a pop-up appears above your finger with a `Cog Icon`, and then release the Comma key.
    Upon release a new pop-up should appear directly in the middle of the screen with two options `Languages` and `(AOSP) Android Keyboard Settings`.
    Then press the Keyboard one to open the limited settings menu. (Even if you needed to go to `Languages` its better to go to keyboard first)

[Soft Reset]
    If your table is already setup you can from the dashboard tap the `Gear` icon in the Top-Right Corner
    Tap `Stats`, and then tap `Advanced` and select `Factory Data Reset`, then follow the prompts.

[Hard Reset]
    If you table is not setup or is bricked, from a powered-down state, hold the `Volume Up` and `Volume Down` buttons, then hold the `Power` button.
    Continue holding, even after the screen turns on, and remain holding until the `Recovery Mode` menu appears, then you may release the buttons.
    Using the `Volume Keys` to move selection and the `Power` key as `Select`, Go to `Factory Data Reset`, and follow the prompts.
    Once the reset has finished, go to `Restart Device Now` and accept.
```

---

### The Guide ###

#### Step 1: The Keyboard ####

WARNING: This WILL require a Factory Data Reset of the Infinity Table. Backup any data before you begin!
This is purely expiremental and no stable build will ever be produced.
Crashes and Complete Failures are expected to happen seemingly with or without cause

##### 1.1 The FKing Pain #####

```ini
[Access Keyboard Settings Icon]
    The first screen you see should be for connecting to a WiFi Network. Do NOT connect yet! Instead, tap a random SSID to pop-up the virtual keyboard.
    If you have access to the `AOSP Android Keyboard`, noted by a full-device-width & white background gui, then we are properly in the stock OS version. Now we do the Comma-Trick from the section above to open the limited-settings menu.
    Now that your into the Settings Menu, select `Input Styles and Themes` (sometimes labeled `Input & Layout`) and after, in the Top-Right Corner there will be a very hard to see, white `+` icon sitting on the also white banner, select this.
    A pop-up mid-screen will appear and their will be 2 Fields, `Language` and `Layout` followed by a row of buttons like `Remove`, `ADD`, and `SAVE`. For Language, scroll to the very bottom and select `No Language (Alphabet)`. (You can use your native language for the language section but weve found more compatability using None)
    Then for layout select `PC`, no exceptions, then click `ADD` or `SAVE`. A warning should immediatly pop-up about enabeling the layout. Click `Enable Now`.
    You should be redirected to what looks like the `Languages` Settings Menu (but it isnt), and here you will typically see the first option be something like `Use Device Default` and is the only active option. Everything else is grayed-out.
    Turn this default option off, and at that moment all the other options should no longer be grayed-out, and a random one from the list should get toggled. First! Find the option for the layout we just created, typically shows up as `Alphabet (PC)` (or `<YOUR_LANGUAGE> (PC)` if you didnt go with no language) and enable it. THEN, disable the others and ensure ours is the ONLY one enabled. (If you disable everything settings will auto-reenable the default and gray-out the bottom section again, so find your added layout FIRST, THEN remove the rest)
    Now, use the Navigation Buttons to return back to our `Input Styles and Themes` menus, and long-click all the other layouts that are listed, then click `Remove` on their pop-ups. Ensure only our custom layout is present.
    Now the annoying part. Youll notice there is no longer any Navigation Buttons. Most setting menus while pre-exploited are like this and so the ONLY way to get out is you HAVE to reboot.
    After rebooting, use the comma-trick again to get the settings pop-up and this time go into `Languages`. (Languages is also a field in AOSP Keyboard Settings so you can click either one)
    And now just like before when enabeling the custom layout, you should see a single active option labeled `Use Device Default` with many others grayed-out underneath it.
    Once again disable the default, and enable our custom layout, and then disable all others leaving only `Alphabet (PC)` as the enabled option.
    After this, yes, you have to reboot again, but we now got the minimal requirements to move on with the exploit.
```

##### 1.2 Verify or VeriCry #####

```ini
[Verify]
    Now after reboot, just trigger the keyboard to pop-up and then you should quickly see that the gui looks slightly different now.
    In the Bottom-Left corner there should now be a `Cog Icon`. DONT ENTER IT YET! But this is required, and if you do not have this Icon, you will most likely have to do a Hard Factory Reset and try again.
    But if you do have this icon. Congrats! We can now move onto Step 2!
```

---

#### Step 2: Accessing Android Settings ####

```ini
[!!WARNING!!]
    This next step is all about timing. So read this section entirely and understand what you have to do before trying it.
    If not completed quickly enough on the very first try. The dashboard WILL update, typically you have ~3s or less, and it completely removes the Android Keyboard with a replacement Infinity Keyboard which patches this exploit.
    If this happens at ANY time going forward, HURRAY! Your Factory Resetting and Trying again! But as long as your in these settings menus, even if the keyboard updates (and it will), we are okay!

[Time Attack Settings]
    Now, finally connect to your preferred WiFi Network and allow the Dashboard to update.
    The second it finishes the screen will flash a couple times and then it brings you to a Welcome! & Sign-In page.
    This page is what we need to Time Attack and get away from ASAP.
    So The instant this page pops up, as quickly as possible click anything that will make the keyboard appear, then hit that new `Cog Icon` in the bottom left corner to cause the Mid-Screen pop-up to appear.
    Then click any one these to go into the settings menu just like before. If you cannot make it to one of these menus before the keyboard updates, Factory Reset & ReTry is required. (The updated keyboard is NOT full-device-width and has a black background so youll know immediatley when it updates)
    Again the KEY thing here is getting into those settings menus BEFORE the keyboard updates.
    Once in the settings, if you are not in `Languages` already, select this option. Now in the Top-Right corner you should see a `Search Icon`.
    If you click this and type a letter, youll notice the search results returns the full Standard Android Settings list, which is precisely what we need.
    If your in the Full Android Settings Screen congrats! The Finiky and Manual Hard stuff is out of the way! Now its all down to setting up the Environment down to the last settings, line of code, and boot-jobs
```

---

#### Step 3: Setting the Settings ####

##### 3.1 Dev Access #####

```ini
[Dev Access]
    Now the rest of these steps should feel just like every other android on the market. Except that you CANNOT leave settings. If you do. Factory Reset and try again is required.
    First, in the search bar, type `ab`, and you should get the result `About Tablet` (or `About Device`). Select this and scroll to the very bottom, looking for the entry labeled `Build Number`. It will ALWAYS be labeled `Build Number`
    Tap this label 10X in rapid succession or until a pop-up appears saying `You are now a developer`.
    Now in the search bar type `apps` and look for `Apps & Notifications`. Select this and you should get a new settings menu that has a `Show All Apps` button towards the top. If you do not have this, re-search `apps` again and pick a different `Apps & Notifications` option. (One does permissions and one does App Info. We need the info one)
    Now on the list of all installed apps, look for `Infinity Keyboard` and select this. First select `Force Stop`, then `Disable`, then `Uninstall`. (Going our of order can sometimes make dashoard attempt an update again which will force you to Reset and Try Again)
    Now. SLOWLY. Keep pressing the back arrow until we arrive back at the Limited-Settings menu, and DO NOT go any further. Once there, go back to `Languages` if not already, and click the `Search Icon` again. (This lets the Settings Options update with the new Dev Options)
    Now type `Dev` and you should get an option called `Developer Options`. Select this. In the following settings menu we have a few things to set, order doesnt matter, but each one MUST be set
```

##### 3.2 Reuired Settings #####

```ini
[Dev Settings --REQUIRED]
    USB Debugging = Enabled
    Wireless Debuging = Enabled
    Disable ADB Authentication Timeout = Enabled
    System Auto Updates = Disabled (its still going to try on every reboot)
    Force Allow Apps on External = Enabled
    USB Default Configuration = File Transfer (sometimes labeled as Media/Photo Transferring)

[System Settings --REQUIRED]
    System Navigation = Gesture
    Default Keyboard = Android Keyboard (`(AOSP) Android Keyboard`)
```

##### 3.3 Useful Extra Settings #####

```ini
[Note]
    After you made all of these changes, we should go back to `Input and Layout` and add our custom No Language & PC layout again
    Then yes, go and re-do the enabled layouts and enabled languages the exact same as before so that our keyboard always has the `Cog Icon` giving us an entry-point to settings.
    Sometimes `Languages` wont show the Layout as an option and this is fine. Just select your normal language in this case. The most important thing is that it is NOT set to `Use System Default`
    And this time we actually have Navigation Buttons on every menu! Hurray!
    This step is not Mandatory but Very STRONGLY recommended. Likewise, the remaining options in this step are just optional.
    They may but probably wont affect the exploit in anyway, but we listed them anyways as they tend to make controlling the table after exploit more robust and fail proof

[Dev Settings]
    Show Taps = Enabled
    Show Pointer Location = Enabled
    Logging Level = Verbose
    Double Space Period = Disabled
```

---

#### Step 4: ADB Debugging --No Forgiveness ####

```ini
[Notes on ADB]
    Now the real challange and coding/scripting begins.
    You will require a second device with up-to-date ADB binaries and USB3.0 (or better) ports (and a USB-A Male to USB-A Male Cable) or LAN Access and a Strong WiFi Controller & Driver
    We need to build a bridge into the Tables adbd shell so we can make the final requied adjustments and break this table free.
    There is two main methods of doing this. USB across USB Debugging. Or with LAN across Wireless Debugging.
    Weve had more success using Wireless Debugging but attempting USB first is always recommended as its much easier to connect.
    For USB to work it MUST be using USB3.0 or better ports. (So the Tables BLUE usb port and your connected-devices 3.0 port).
    And the cable used must be a Thunderbolt cable with File Transfer Support. Most `High Speed` Braided Cables will work for this, but if the cable feels `'thin'` it probably wont
    For Wireless to work. Both devices MUST be on the same WiFi Network and visible to eachother. It helps if both devices have up-to-date system packages and the Host Device has up-to-date adb binaries

[USB Method]
    To Restate. Connect a USB3.0 Thunderbolt or Better USB-A Male to USB-A Male cable into the Blue USB port on the Table and into an equivelant port on the host device.
    Once connected. On the Host Device, access a terminal and type `adb devices` then wait a few moments for adb daemon to start, and to check for connections.
    If nothing appears in the resulting `Connected Devices` list, you can try changing usb ports / updating software but more than likely youll be using the Wireless Method instead.
    If a device does appear, pat your own back! You saved yourself the Wireless Debugging headache! Note the Device-ID that was given by adb and your now ready for the next step

[Wireless Method]
    To Restate. Both Devices MUST be on the same WiFi Network and have decent WiFi Controllers and Drivers. Too slow of a driver and adb will drop the connection off and on.
    This method seems to have better success with being able to connect but it is a pain to do.
    First. On the Table. Go back to the `Developer Options` and find the Wireless Debugging option again. This time, click and hold the text of this option (not the button toggle) then release
    This should redirect you to a Wireless Debugging Connections Menu, and towards the bottom there should be a `Pair Device with Pairing Code` option or something along those lines. Go ahead and select this then leave the pop-up and table alone
    Now in small text, towards the bottom of the pop-up, you should see a string that denotes the Tables IP_Address and exposed Port. it should look something like this 10.0.234:92846 (<IP_Address>:<Port>)
    In your Host Terminal type `adb pair "$IP_Address":"$Port"` and hit enter. If entered correctly it will immediatly ask for the Code / Pin.
    The code is the Large 6-Digit Pin on the Tables pop-up. Go ahead and enter this pin to your terminal, and note. Since this is technically a `passphrase` the terminal will not show any signs that you typed anything at all.
    So it easiest to type the pin slow and accurate then hit enter. If you get lost at any point the best corse is to press CTRL+C cancelling the Code Entry, then close the pop-up on table, and re-open another one by pressing `Pair with Code/Pin` again. (This will change the exposed Port everytime so always check this)
    If entered correctly, and given some time to authenticate. You should recieve a Success print in the console, and the table should have automatically closed the last pop-up.
    If so your ready to connect adb finally by noting the IP_Address and Port that is listed towards the top of the Wireless Debugging Connections menus. (throughout all this, the IP_Address will rarely change, but the Port will always change)
    Then in terminal type `adb connect "$IP_Addres":"$New_Port"` and hit enter. If correct you should quickly recieve a Succefully connected message.
    If so, verify connection by typing `adb devices` in the terminal and seeing if the entered Ip_Address:Port gets listed as an `Active` Connected Device.
    When you see this your good to make the final system change by typing `adb tcpip 5555` and waiting roughly 30s. Your adb connection should drop sometime after this.
    Once it drops just type `adb connect "IP_Address":5555` and hit enter. You should quickly get a Successfully connected message again and you are now FINALLY done connecting ADB
```

#### Step 5: Bypass OEM Software ####

```ini
[Note]
    Now we are on the Last step for Bypassing the OEM Software entirely, and one more step away from Persistence and Cross-Boot Support.
    What you NEED to install at minimum is a new Andriod Launcher Application, A new File Manager, and a New App-Store.
    We have tested a bunch and came to like the following APKs (Repo builds and updates will use these as defaults)

[Suggested]
    MiniDesktop (tinylauncer) as a SuperLite Launcher Application
    F-Droid & Aurora Store as App-Stores
    FX Explorer as the File Manager
    Tasker + Auto-Tap Extension + Termux-Tasker (This is the only Paid Service and NOT required)

[Required] # Theyre Free AND Open Source!
    Termux-App (Required) # The Executor
    Termux-Api (Required) # The Device Controller
    Termux-Boot (Required) # The Boot-Persistence Enforcer
```

#### Step 6: Termux & Launcher Init ####

The rest of this is almost entirely bash scripting. The following is NOT the only way to do this but it is the most stable we have found.
If you dont already have at least intermediate bash knowledge and some systems knowledge. We HIGHLY suggest to just stick with the default we provide and not finik too much.
But if you are a bash-chad, then you'll see what were doing by reading the minimal setup below and can go make your own scripts, or even contribute your own to the repo!
Anyways. Let the Syntax Errors begin.

In your terminal type `adb shell monkey -p com.termux 1` and hit enter. This should force open the Termux app for you, and after intializing, drop you into a Termux-Terminal.
in Termux now. Youll want to type the following to do a quick and minimal setup that termux needs to interact with the table.

```bash
termux-change-repo # And then follow the On-Screen GUI to select an appropiate repo
termux-setup-storage # And then follow the pop-up Prompt or click allow. which ever way it presents itself
```

Now back at the Host Terminal type `adb shell monkey -p com.termux.api 1` to force open termux-api and enumerating it to the device. Follow any Setup Instructions found within the app.
Next, back at the Host terminal again run `adb shell monkey -p com.termux.boot 1` to again for open termux-boot, and following any Setup instructions found inside this app.
If you also installed Termux-Tasker repeat the same process again but for all 3 apps. termux-tasker, tasker, and auto input (auto tap)
Once these have been opened and setup per instructions. We need to set their permissions in settings.
So back at the Host Terminal run `adb shell am start android.settings.SETTINGS` to force open the Settings Menu again and now search for `Apps` and find the same `Apps & Notifications` we did before.
Then look for termux, termux-api, and termux-boot, etc... And in each one we want to grant every permission listed under permissions. Then we want to select `Advanced` and `Battery Optimization`.
In Battery Optimization, how the Table displays the apps is weird, so switch between whatever two filter options it gives you until you find the target apps again.
Once found ensure that each one is NOT optimizing their battery usage.
Then. Whatever launcher app you decided to install needs to be set as the Default Home by searching `default` in the search bar and selecting `default apps`
Scroll through the options until you either find `Home` or the launcher app icon itself.
If you found the `Home` option click this, and just make sure that your launcher is selected.
If you found the apps icon click it. and go through all its menu's until you find `Home` listed somewhere. You should be able to just click it and the table will automatically set it as default Home now.

Congrats!!
You have offically now jailbroken the table at its bare minimum and can install ANY android game thats version compatible and play. (We've even played PUBG and Minecraft with a Controller & Touch)
However. Please note stopping here ensures you'll be doing all this again one day when either 1upArcade releases another update. Or the table randomly runs a soft-update in the background and re-installes the patched keyboard again

##### Step 7: Fix-It Boot Scripts #####

This is where the peristance and bash heavyness of this project comes from. We need a script to always trigger on boot, that will detect if the table even tried an update or if any settings get reset.
Then auto removes / resets them immediatly giving you back your jailbroken device in the same environment.

so the rest of this is ALL on the Table in Termux

```bash
mkdir -p "$HOME.termux/boot" "$HOME/.termux/logs" "$HOME/.local/bin" "$HOME/.config"
touch "$HOME/.termux/logs/boot.log"
touch "$HOME/.termux/boot/startup"
chmod +x "$HOME/.termux/boot/startup"
nano "$HOME/.termux/boot/startup"
```

in the nano editor type

```bash
#!/data/data/com.termux/files/usr/bin/bash
VERSION='0.1'

LOG="$HOME/.termux/logs/boot.log"

# Helpers
ts(){
    date "+%Y-%m-%d %H:%M:%S"
}

error(){
    local msg="$1"
    termux-toast "[ERROR]: $msg"
    echo "$(ts) [ERROR]: $msg"
    sleep 5
}

warn(){
    local msg="$1"
    termux-toast "[WARN]: $msg"
    echo "$(ts) [WARN]: $msg"
    sleep 3
}

info(){
    local msg="$1"
    termux-toast "[INFO]: $msg"
    echo "$(ts) [INFO]: $msg"
    sleep 1
}

run(){
    local desc="$1"
    shift
    local cmd="$*"
    local out
    if ! out=$(bash -c "$cmd" 2>&1); then
        error "$desc failed: $out"
        return 1
    else info "$desc success"
        echo "$(ts) [RUN ] $cmd"
        echo "$(ts) [RUN ] $out"
        return 0
    fi
}

# Main Pipe
{
    # Remove OEM
    run "Fix-It v$VERSION - Termux-Boot Started $(date)" "termux-wake-lock"
    for pkg in "${PAKS[@]}"; do
        if pm list packages | grep -q "$pkg"; then
            warn "Found OEM Package $pkg"
            run "Disabeling" "pm disable-user --user 0 $pkg"
        else info "Package $pkg Not Found"
        fi
    done

    # Ensure Settings
    # Keyboard
    run "Setting AOSP as default" "settings put secure default_input_method $AOSP"

    # Debugging
    run "Enabeling USB & Debugging" "settings put global adb_enabled 1"
    run "Enabeling Wireless Debugging" "settings put global adb_wifi_enabled 1"

    # Unkown Installs
    run "Allowing Installs from Unkown Sources" "settings put secure install_non_market_apps 1"

    # Stop Updates
    run "Disabeling Auto System Udpates" "settings put global auto_update_system 0"
    run "Disabeling OTA Updates" "settings put global ota_disable_automatic_update 1"

    # Launcher
    run "Enabeling TinyLauncher" "pm enable com.atomicadd.tinylauncher"
    run "Setting TinyLauncher as Default Home" "setting put secure prefferred_launcher com.atomicadd.tinylauncher/.MainActivity"

    info "Termux-Boot: Fix-It Pipeline Finished $(date)"
} >> "$LOG" 2>&1
```
