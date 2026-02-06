# -*- coding: utf-8 -*-
import naoqi
import time
import urllib2
import uuid
import cv2
import numpy as np
import json
import base64
import config



class MathRobot(naoqi.ALModule):
    def __init__(self):

        self.module_name = "MathRobot_" + str(int(time.time()))
        naoqi.ALModule.__init__(self, self.module_name)

        # NASTAVENÍ ?E?I
        self.tts = naoqi.ALProxy("ALTextToSpeech")
        self.tts.setLanguage("Czech")
        self.tts.setParameter("speed", 70)
        self.tts.setParameter("pitchShift", 1)

        # NASTAVENÍ HLASITOSTI
        self.audio = naoqi.ALProxy("ALAudioDevice")
        self.audio.setOutputVolume(50)


        # MAKE PEPPER STAND UP AT START
        self.awarnes = naoqi.ALProxy("ALBasicAwareness")
        self.awarnes.setEnabled(False)
        self.posture = naoqi.ALProxy("ALRobotPosture")
        self.posture.goToPosture("StandInit", 0.5)
        time.sleep(1)  # let posture stabilize

        # CAMERA SUBSCRIBTION
        self.video = naoqi.ALProxy("ALVideoDevice")
        camera_name = "touch_cam_" + str(int(time.time() * 1000))  # milliseconds
        self.cam = self.video.subscribeCamera(
            camera_name,
            0,      # top camera
            2,      # VGA
            13,     # RGB/BGR
            5       # FPS
        )
        # TABLET SUBSCRIPTION
        self.tabletService = naoqi.ALProxy("ALTabletService")

        self.tabletService.enableWifi()
        self.tabletService.showWebview(config.WEB_FOR_TABLET)

        self.tts.say("Pohlad´ mě po hlavě a já ti spočítám příklad.")

        # CUSTOM HEAD TOUCH LISTENER
        self.memory = naoqi.ALProxy("ALMemory")
        while True:
            time.sleep(0.01)
            value = self.memory.getData("MiddleTactilTouched")
            if value == 1.0:
                self.onMiddleTouched()

    # -------------------------------------------------------------------
    def capture_image(self):
        img = self.video.getImageRemote(self.cam)
        if img is None:
            print("NO IMAGE")
            return None

        width, height = img[0], img[1]
        data = img[6]

        arr = np.frombuffer(data, dtype=np.uint8).reshape((height, width, 3))
        out_path = "output_rgb.jpg"
        cv2.imwrite(out_path, arr)
        ok, jpg = cv2.imencode(".jpg", arr)
        if not ok:
            print("JPEG ENCODE ERROR")
            return None

        return jpg.tobytes()

    # -------------------------------------------------------------------
    def send_image(self, jpeg_bytes):
        import base64
        import json
        import urllib
        import urllib2

        boundary = "----PepperBoundary" + uuid.uuid4().hex

        body_start = (
            "--" + boundary + "\r\n"
            "Content-Disposition: form-data; name=\"file\"; filename=\"pepper.jpg\"\r\n"
            "Content-Type: image/jpeg\r\n\r\n"
        ).encode("utf-8")

        body_end = ("\r\n--%s--\r\n" % boundary).encode("utf-8")

        body = body_start + jpeg_bytes + body_end

        # ----- Basic Auth header -----
        raw = "test:test"
        auth_header = "Basic " + base64.b64encode(raw)

        headers = {
            "Content-Type": "multipart/form-data; boundary=%s" % boundary,
            "Content-Length": str(len(body)),
            "User-Agent": "PepperRobot/2.0",
            "Authorization": auth_header,
        }

        req = urllib2.Request(config.API_URL, data=body, headers=headers)

        try:
            response = urllib2.urlopen(req, timeout=20)

            resp_text = response.read()

            print("SERVER RESPONSE:", resp_text)

            try:
                resp_json = json.loads(resp_text)
                if resp_json.get("results") and len(resp_json["results"]) > 0:
                    result_filtered = resp_json["results"][0].get("result_filtered")
                    result_filtered = result_filtered.encode("utf-8")

                    # RESULT
                    result_filtered = result_filtered.rstrip(".")
                    print("Výsledek: ", result_filtered)
                    self.tabletService.reloadPage(True)
                    self.tts.say(result_filtered)


            except Exception as e:
                print("Error sending result_filtered:", e)

        except urllib2.HTTPError as e:
            print("\n--- HTTP ERROR ---")
            print("Status:", e.code)
            print("Reason:", e.reason)
            try:
                print("Response body:", e.read())
            except:
                print("error")
    # -------------------------------------------------------------------

    def onMiddleTouched(self):
        print("Middle tactile touched")

        # Capture image
        print("Taking photo")
        img = self.capture_image()
        if img:
            print("Sending photo...")
            self.send_image(img)

# -----------------------------------------------------------------------

myBroker = naoqi.ALBroker("myBroker", "0.0.0.0", 0, config.ROBOT_IP, config.ROBOT_PORT)

global MathRobot
MathRobot = MathRobot()  # prom?nná je v?dy global a jmenuje se stejn? jako t?ída


try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    myBroker.shutdown()
