#!/usr/bin/env python
import sys
import socket
import time
import getopt

def usage():
  print("HP 8657B Control Program")
  print("Options:")
  print("* = Required")
  print("  -h / --help          - Print this help message")
  print("* --ip=                - IP Address of the GPIB Interface")
  print("  --port=              - TCP Port of the GPIB Interface. Defaults to 1234")
  print("  --gpibaddr=          - GPIB Address of the instrument. Defaults to 7")
  print("  --frequency=         - Frequency (in MHz) to be set. E.G. '100.0'")
  print("  --amplitude=         - Amplitude (in dBm) to be set. E.G. '-37.0'")
  print("  --rf=                - Enable/Disable the RF output. Accept 'on'/'off'/'dead'")
  print("  --mod=               - Enable/Disable Modulation. Accepts 'am'/'fm'/'off'")
  print("  --modsrc=            - Set/Disable Modulation Sources. Accepts 'ext'/'dcext'/'1000'/'400'/'off'")
  print("  --moddev=            - Set Modulation Deviation (in KHz). E.G. '5.0'. FM Modulation Only.")
  print("  --modpct=            - Set Modulation Percent (in Percent) E.G. '75'. AM Modulation Only.")
  sys.exit()

def main(argv):
  tcp_ip = ''
  tcp_port = 1234
  buffer_size = 1024
  gpib_addr = "7"

  message = ""
  frequency = ""
  amplitude = ""
  rf = ""
  mod = ""
  mod_src = ""
  mod_dev = ""
  mod_pct = ""

  try:
    opts, args = getopt.getopt(argv, "h", ["help","ip=","port=","gpibaddr=","frequency=","amplitude=","rf=","mod=","modsrc=","moddev=","modpct="])
  except getopt.GetoptError as err:
    print str(err)
    usage()
    sys.exit(2)

  for opt, arg in opts:
    if opt == '-h':
      usage()
    if opt == "--ip":
      tcp_ip = arg
    if opt == "--port":
      tcp_port = arg
    if opt == "--gpibaddr":
      gpib_addr = arg
    if opt == "--frequency":
      frequency = arg
    if opt == "--amplitude":
      amplitude = arg
    if opt == "--rf":
      rf = arg
    if opt == "--mod":
      mod = arg
    if opt == "--modsrc":
      mod_src = arg
    if opt == "--moddev":
      mod_dev = arg
    if opt == "--modpct":
      mod_pct = arg

  # Check that we actually got an IP address
  if tcp_ip == "":
    print("ERROR: IP address not specified!")
    usage()

  # Check for options that have to go together
  if any([mod_src, mod, mod_dev, mod_pct]):
    if not all([mod_src, mod, (mod_dev or mod_pct)]):
      print("ERROR: Must specify --mod, --modsrc and --moddev or --modpct.")
      usage()

  # Open our TCP socket
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((tcp_ip, tcp_port))

  # Set the address of the instrument we're talking to
  message = "++addr %d\n" % int(gpib_addr)
  s.send(message)

  # Check for things to actually set
  if frequency != "":
    message = "FR%fMZ\n" % float(frequency)
    s.send(message)
    time.sleep(0.1)
  if amplitude != "":
    message = "AP%fDM\n" % float(amplitude)
    s.send(message)
    time.sleep(0.1)
  if rf != "":
    if rf in ("off", "OFF"):
      message = "R2\n"
    if rf in ("dead", "DEAD"):
      message = "R5\n"
    if rf in ("on", "ON"):
      message = "R3\n"
    s.send(message)
    time.sleep(0.1)
  if mod_src != "":
    if mod_src in ("off", "OFF"):
      message = "S4\n"
    if mod_src in ("ext", "EXT"):
      message = "S1\n"
    if mod_src in ("dcext", "DCEXT"):
      message = "S5\n"
    if mod_src == "1000":
      message = "S3\n"
    if mod_src == "400":
      message = "S2\n"
    s.send(message)
    time.sleep(0.1)
  if mod != "":
    if mod == "0":
      message = "S4\n"
    if mod in ("am", "AM"):
      message = "AM\n"
    if mod in ("fm", "FM"):
      message = "FM\n"
    s.send(message)
    time.sleep(0.1)
  if mod_dev != "":
    message = "%fKZ\n" % float(mod_dev)
    s.send(message)
    time.sleep(0.1)
  if mod_pct != "":
    message = "%fPC\n" % float(mod_pct)
    s.send(message)
    time.sleep(0.1)

  # We're done, close the socket and quit
  s.close()
  sys.exit()

if __name__ == "__main__":
  main(sys.argv[1:])
