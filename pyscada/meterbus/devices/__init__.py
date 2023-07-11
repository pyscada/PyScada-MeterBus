# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .. import PROTOCOL_ID
from pyscada.device import GenericHandlerDevice

import traceback
from time import time, sleep
import simplejson as json
import yaml
from decimal import Decimal

import logging

logger = logging.getLogger(__name__)

try:
    import serial
    import meterbus

    driver_ok = True
except ImportError:
    logger.error("Cannot import meterbus or serial")
    driver_ok = False


class GenericDevice(GenericHandlerDevice):
    def __init__(self, pyscada_device, variables):
        super().__init__(pyscada_device, variables)
        self._protocol = PROTOCOL_ID
        self.driver_ok = driver_ok

    def connect(self):
        """
        establish a connection to the Instrument
        """
        super().connect()
        result = True

        try:
            ibt = meterbus.inter_byte_timeout(self._device.meterbusdevice.baudrate)
            self.inst = serial.serial_for_url(
                self._device.meterbusdevice.port,
                self._device.meterbusdevice.baudrate,
                8,
                "E",
                1,
                inter_byte_timeout=ibt,
                timeout=self._device.meterbusdevice.timeout,
            )
            if self.inst is not None and ping_address(
                self.inst,
                self._device.meterbusdevice.address,
                self._device.meterbusdevice.retries,
                self._device.meterbusdevice.read_and_ignore_echo,
            ):
                logger.debug("Ping success to meterbus device : %s" % self.__str__())
        except serial.serialutil.SerialException as e:
            self._not_accessible_reason = e
            result = False

        self.accessibility()

        return result

    def disconnect(self):
        if self.inst is not None:
            self.inst.close()
            self.inst = None
            return True
        return False

    def read_data(self, variable_instance):
        """
        read values from the device
        """

        variable_instance.echofix = variable_instance.read_and_ignore_echo
        variable_instance.device = variable_instance.port
        variable_instance.output = "dump"
        dump = None

        try:
            dump = do_char_dev(self.inst, variable_instance)
            # logger.debug(dump)
        except Exception:
            logger.error(traceback.format_exc())

        return dump


# From mbus-serial-request-data.py from pyMeterBus/tools
# https://github.com/ganehag/pyMeterBus/blob/master/meterbus/tools/mbus-serial-scan.py


def ping_address(ser, address, retries=5, read_echo=False):
    for i in range(0, retries + 1):
        meterbus.send_ping_frame(ser, address, read_echo)
        try:
            frame = meterbus.load(meterbus.recv_frame(ser, 1))
            if isinstance(frame, meterbus.TelegramACK):
                return True
        except meterbus.MBusFrameDecodeError as e:
            pass

        sleep(0.5)

    return False


def do_reg_file(args):
    with open(args.device, "rb") as f:
        frame = meterbus.load(f.read())
        if frame is not None:
            print(frame.to_JSON())


def do_char_dev(ser, args):
    try:
        address = int(args.address)
        if not (0 <= address <= 254):
            address = args.address
    except ValueError:
        address = args.address.upper()

    try:
        # ibt = meterbus.inter_byte_timeout(args.baudrate)
        # with serial.serial_for_url(args.device,
        #                           args.baudrate, 8, 'E', 1,
        #                           inter_byte_timeout=ibt,
        #                           timeout=args.timeout) as ser:
        frame = None

        if meterbus.is_primary_address(address):
            if ping_address(ser, address, args.retries, args.echofix):
                meterbus.send_request_frame(ser, address, read_echo=args.echofix)
                frame = meterbus.load(
                    meterbus.recv_frame(ser, meterbus.FRAME_DATA_LENGTH)
                )
            else:
                logger.warning(
                    "Ping failed for MeterBus device with primary address : {}".format(
                        address
                    )
                )

        elif meterbus.is_secondary_address(address):
            if ping_address(
                ser, meterbus.ADDRESS_NETWORK_LAYER, args.retries, args.echofix
            ):
                meterbus.send_select_frame(ser, address, args.echofix)
                try:
                    frame = meterbus.load(meterbus.recv_frame(ser, 1))
                except meterbus.MBusFrameDecodeError as e:
                    frame = e.value

                # Ensure that the select frame request was handled by the slave
                assert isinstance(frame, meterbus.TelegramACK)

                meterbus.send_request_frame(
                    ser, meterbus.ADDRESS_NETWORK_LAYER, read_echo=args.echofix
                )

                sleep(0.3)

                frame = meterbus.load(
                    meterbus.recv_frame(ser, meterbus.FRAME_DATA_LENGTH)
                )
            else:
                logger.warning(
                    "Ping failed for MeterBus device with secondary address : {}".format(
                        address
                    )
                )

        if frame is not None and args.output != "dump":
            recs = []
            for rec in frame.records:
                recs.append({"value": rec.value, "unit": rec.unit})

            ydata = {
                "manufacturer": frame.body.bodyHeader.manufacturer_field.decodeManufacturer,
                "identification": "".join(
                    map("{:02x}".format, frame.body.bodyHeader.id_nr)
                ),
                "access_no": frame.body.bodyHeader.acc_nr_field.parts[0],
                "medium": frame.body.bodyHeader.measure_medium_field.parts[0],
                "records": recs,
            }

            if args.output == "json":
                return json.dumps(ydata, indent=4, sort_keys=True)

            elif args.output == "yaml":

                def float_representer(dumper, value):
                    if int(value) == value:
                        text = "{0:.4f}".format(value).rstrip("0").rstrip(".")
                        return dumper.represent_scalar("tag:yaml.org,2002:int", text)
                    else:
                        text = "{0:.4f}".format(value).rstrip("0").rstrip(".")
                    return dumper.represent_scalar("tag:yaml.org,2002:float", text)

                # Handle float and Decimal representation
                yaml.add_representer(float, float_representer)
                yaml.add_representer(Decimal, float_representer)

                return yaml.dump(
                    ydata, default_flow_style=False, allow_unicode=True, encoding=None
                )

        elif frame is not None:
            return frame.to_JSON()

    except serial.serialutil.SerialException as e:
        logger.warning(e)
