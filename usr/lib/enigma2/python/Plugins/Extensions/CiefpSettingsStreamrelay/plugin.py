from Plugins.Plugin import PluginDescriptor
from enigma import eTimer, ePicLoad
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Button import Button
from Components.Pixmap import Pixmap
from Tools.Directories import fileExists
from Tools.LoadPixmap import LoadPixmap
import logging
import os
import re

# Plugin Descriptor
PLUGIN_NAME = "CiefpSettingsStreamrelay"
PLUGIN_VERSION = "1.3"
PLUGIN_DESC = "Convert bouquets for StreamRelay."
PLUGIN_ICON = "/usr/lib/enigma2/python/Plugins/Extensions/CiefpSettingsStreamrelay/icon.png"
PLUGIN_PATH = "/usr/lib/enigma2/python/Plugins/Extensions/CiefpSettingsStreamrelay"
logger = logging.getLogger("CiefpSettingsStreamrelay")
logger.setLevel(logging.INFO)

class StreamRelayConverter(Screen):
    skin = """
    <screen name="StreamRelayConverter" position="center,center" size="1600,900" title="..:: Ciefp Settings Streamrelay ::..">

        <!-- DESNA POZADINA (iza svega desno) -->
        <widget name="sideBackground" position="1000,0" size="600,800" alphatest="on" zPosition="0" />

        <!-- DESNI TEKST -->
        <widget name="status" position="1020,20" size="560,60" font="Bold;30" foregroundColor="#d5fa02" 
            valign="center" halign="center" transparent="1" zPosition="2" />
        <widget name="info" position="1020,100" size="560,120" font="Bold;30" foregroundColor="#d5fa02" 
            valign="center" halign="center" transparent="1" zPosition="2" />

        <!-- LOGOI (bez preklapanja) -->
        <widget name="astra1Logo" position="0,0" size="1000,400" alphatest="on" zPosition="1" />
        <widget name="astra2Logo" position="0,400" size="1000,400" alphatest="on" zPosition="1" />

        <!-- KEYs -->
        <widget name="key_red" position="0,850" size="400,40" font="Bold;28"
            halign="center" valign="center" foregroundColor="#080808" backgroundColor="#a00000" zPosition="2" />
        <ePixmap pixmap="skin_default/buttons/red.png" position="0,850" size="400,40" alphatest="blend" zPosition="1" />

        <widget name="key_green" position="400,850" size="400,40" font="Bold;28"
            halign="center" valign="center" foregroundColor="#080808" backgroundColor="#00a000" zPosition="2" />
        <ePixmap pixmap="skin_default/buttons/green.png" position="400,850" size="400,40" alphatest="blend" zPosition="1" />

        <widget name="key_yellow" position="800,850" size="400,40" font="Bold;28"
            halign="center" valign="center" foregroundColor="#080808" backgroundColor="#a09d00" zPosition="2" />
        <ePixmap pixmap="skin_default/buttons/yellow.png" position="800,850" size="400,40" alphatest="blend" zPosition="1" />

        <widget name="key_blue" position="1200,850" size="400,40" font="Bold;28"
            halign="center" valign="center" foregroundColor="#080808" backgroundColor="#0000a0" zPosition="2" />
        <ePixmap pixmap="skin_default/buttons/blue.png" position="1200,850" size="400,40" alphatest="blend" zPosition="1" />

    </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session

        self["menu"] = MenuList([("Select Astra 19.2E Bouquet", "19.2E"),
                                 ("Select Astra 28.2E Bouquet", "28.2E")])

        self["status"] = Label("Welcome to Ciefp Settings StreamRelay!")
        self["info"] = Label("Select bouquets to convert.")
        self["astra1Logo"] = Pixmap()
        self["astra2Logo"] = Pixmap()
        self["sideBackground"] = Pixmap()
        self["key_red"] = Button("Cancel")
        self["key_green"] = Button("Start Conversion")
        self["key_yellow"] = Button("Select Astra 19.2E")
        self["key_blue"] = Button("Select Astra 28.2E")

        self["actions"] = ActionMap(["SetupActions", "ColorActions"], {
            "cancel": self.close,
            "green": self.start_conversion,
            "yellow": self.select_bouquet_19e,
            "blue": self.select_bouquet_28e,
            "red": self.close
        })

        self.selected_bouquets = []
        
        self.onLayoutFinish.append(self.loadastra1Logo)
        self.onLayoutFinish.append(self.loadastra2Logo)
        self.onLayoutFinish.append(self.loadSideBackground)

    def loadastra1Logo(self):
        logo_path = os.path.join(PLUGIN_PATH, "astra1logo.png")
        if os.path.exists(logo_path):
            try:
                pixmap = LoadPixmap(logo_path)
                if pixmap and self["astra1Logo"].instance:
                    self["astra1Logo"].instance.setPixmap(pixmap)
            except Exception as e:
                logger.error(f"Error loading plugin astra1logo: {str(e)}")
        else:
            logger.error(f"astra1 logo not found: {logo_path}")        

    def loadastra2Logo(self):
        logo_path = os.path.join(PLUGIN_PATH, "astra2logo.png")
        if os.path.exists(logo_path):
            try:
                pixmap = LoadPixmap(logo_path)
                if pixmap and self["astra2Logo"].instance:
                    self["astra2Logo"].instance.setPixmap(pixmap)
            except Exception as e:
                logger.error(f"Error loading plugin astra2logo: {str(e)}")
        else:
            logger.error(f"astra2 logo not found: {logo_path}")        

    def loadSideBackground(self):
        bg_path = os.path.join(PLUGIN_PATH, "sidebackground.png")
        if os.path.exists(bg_path):
            try:
                pixmap = LoadPixmap(bg_path)
                if pixmap and self["sideBackground"].instance:
                    self["sideBackground"].instance.setPixmap(pixmap)
            except Exception as e:
                logger.error(f"Error loading side background: {str(e)}")
        else:
            logger.error(f"Side background not found: {bg_path}")

    def select_bouquet_19e(self):
        if "19.2E" not in self.selected_bouquets:
            self.selected_bouquets.append("19.2E")
            self["status"].setText(f"Selected bouquets: {', '.join(self.selected_bouquets)}")

    def select_bouquet_28e(self):
        if "28.2E" not in self.selected_bouquets:
            self.selected_bouquets.append("28.2E")
            self["status"].setText(f"Selected bouquets: {', '.join(self.selected_bouquets)}")

    def start_conversion(self):
        if not self.selected_bouquets:
            self["info"].setText("No bouquets selected for conversion.")
            return

        for bouquet in self.selected_bouquets:
            if bouquet == "19.2E":
                self.convert_and_save(
                    bouquet_files=[ 
                        "userbouquet.ciefp_19e_skydemovies.tv",
                        "userbouquet.ciefp_19e_skydedocu.tv",
                        "userbouquet.ciefp_19e_skydesport.tv"
                    ],
                    output_file="userbouquet.ciefp_19e_skyde_icam.tv",
                    header="#NAME • 19,2 E - Sky DE • icam :: streamrelay ::\n"
                )

            if bouquet == "28.2E":
                self.convert_and_save(
                    bouquet_files=[ 
                        "userbouquet.ciefp_28e_skyukmovie.tv",
                        "userbouquet.ciefp_28e_skyukdocuments.tv",
                        "userbouquet.ciefp_28e_skyukkids.tv",
                        "userbouquet.ciefp_28e_skyuksports.tv"
                    ],
                    output_file="userbouquet.ciefp_28e_skyuk_icam.tv",
                    header="#NAME • 28,2 E - SKY UK • icam :: streamrelay ::\n"
                )

        self.session.openWithCallback(
            self.confirm_restart,
            MessageBox,
            "Conversion complete.\nDo you want to restart Enigma2?",
            MessageBox.TYPE_YESNO
        )

    def convert_and_save(self, bouquet_files, output_file, header):
        converted_lines = []
        for bouquet_file in bouquet_files:
            bouquet_path = os.path.join("/etc/enigma2", bouquet_file)
            if fileExists(bouquet_path):
                with open(bouquet_path, "r") as f:
                    lines = f.readlines()

                for i, line in enumerate(lines):
                    if line.startswith("#SERVICE 1:64:"):
                        converted_lines.append(line)
                        if i + 1 < len(lines) and lines[i + 1].startswith("#DESCRIPTION"):
                            converted_lines.append(lines[i + 1])
                        continue

                    if line.startswith("#SERVICE"):
                        original_reference = line[len("#SERVICE "):].strip()
                        channel_name = self.get_channel_name_from_reference(original_reference)
                        converted_line = self.process_service_line(line, original_reference, channel_name)
                        converted_lines.append(converted_line)

        output_path = os.path.join("/etc/enigma2", output_file)
        with open(output_path, "w") as f:
            f.write(header)
            f.writelines(converted_lines)

    def get_channel_name_from_reference(self, service_reference):
        # Ekstrahujemo 4 relevantna polja iz service_reference
        parts = service_reference.split(":")
        if len(parts) < 8:
            print(f"Invalid service reference format: {service_reference}")
            return "Invalid Reference"

        # Formatiramo referencu za pretragu u lamedb
        relevant_reference = f"{int(parts[3], 16):04x}:{int(parts[6], 16):08x}:{int(parts[4], 16):04x}:{int(parts[5], 16):04x}"
        print(f"Formatted relevant reference for search: {relevant_reference}")

        lamedb_path = "/etc/enigma2/lamedb"
        if not fileExists(lamedb_path):
            print("lamedb file not found.")
            return "Unknown Channel"

        try:
            with open(lamedb_path, "r") as f:
                content = f.read()

            entries = content.splitlines()  # Delimo sadržaj po linijama
            print(f"Loaded lamedb content with {len(entries)} lines.")

            # Iteriramo kroz linije u `lamedb` da pronađemo referencu
            for i in range(len(entries) - 2):
                if entries[i].startswith(relevant_reference):  # Prva linija mora sadržati referencu
                    channel_name = entries[i + 1].strip()  # Druga linija je naziv kanala
                    print(f"Reference {relevant_reference} found at line {i+1}. Channel name: {channel_name}")
                    return channel_name

        except Exception as e:
            print(f"Error reading lamedb: {e}")

        print(f"Service reference {relevant_reference} not found in lamedb.")
        return "Unknown Channel"

    def process_service_line(self, line, original_reference, channel_name):
        parts = line.split(":")
        if len(parts) > 6:
            parts[6] = "21"
        converted_line = ":".join(parts).strip()
        converted_line += "http%3a//127.0.0.1%3a17999/"
        converted_line += original_reference.replace(":", "%3a") + ":"
        converted_line += channel_name
        description_line = f"#DESCRIPTION {channel_name}"
        return converted_line + "\n" + description_line + "\n"

    def confirm_restart(self, answer):
        if answer:
            os.system("killall -9 enigma2")

def main(session, **kwargs):
    session.open(StreamRelayConverter)

def Plugins(**kwargs):
    return [PluginDescriptor(
        name=f"{PLUGIN_NAME} v{PLUGIN_VERSION}",
        description=PLUGIN_DESC,
        where=PluginDescriptor.WHERE_PLUGINMENU,
        icon=PLUGIN_ICON,
        fnc=main
    )]