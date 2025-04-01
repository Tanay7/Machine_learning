# Spacecraft-Inspired Telemetry Transmitter (TelemetryTx.ino)

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) ## Overview

This Arduino sketch simulates a telemetry transmitter inspired by spacecraft communication systems. It gathers data from various onboard sensors, structures this data into a format resembling a CCSDS (Consultative Committee for Space Data Systems) Application Packet (AP), applies Reed-Solomon Forward Error Correction (RS-FEC) for enhanced data integrity, and transmits the processed data over a LoRa radio link.

This project serves as an educational tool to demonstrate key concepts used in space communication, drawing parallels with missions like Voyager 1 in terms of telemetry structuring and the necessity of robust error correction.

## Features

* **Multi-Sensor Integration:** Reads data from the following sensors:
    * BME280: Environmental sensor (temperature, pressure, humidity, altitude).
    * QMC6310: Magnetometer (magnetic field readings).
    * QMI8658: Inertial Measurement Unit (IMU) (acceleration, gyroscope, temperature).
    * GPS Module: Extracts location, altitude, date, time, satellite count, and HDOP using TinyGPS++.
    * Power Management Unit (PMU): Monitors battery voltage, charge percentage, charging status, VBUS voltage, and system voltage.
* **CCSDS-like Packetization:** Structures sensor data and metadata into a C struct (`CCSDSPacket`) that mimics the structure of a CCSDS Application Packet, including:
    * Packet Version Number
    * Type Indicator
    * APID (Application Process Identifier)
    * Sequence Count
    * Packet Length
    * Spacecraft Identifier
    * Mission Time
    * Sensor Readings
    * CRC-16 Checksum
* **Reed-Solomon FEC:** Implements RS(255, 223) encoding to add redundancy to the telemetry data, making it more resilient to transmission errors over the LoRa channel.
* **LoRa Transmission:** Utilizes the RadioLib library to configure and transmit the encoded telemetry data using an SX1262 LoRa transceiver on the 433 MHz band. Configurable transmission parameters include power, spreading factor, bandwidth, and coding rate.
* **GPS Data Handling:** Parses NMEA sentences from a connected GPS module using the TinyGPS++ library.
* **PMU Monitoring:** Reads and includes data from a board-specific Power Management Unit (PMU) object.
* **Data Integrity:** Includes a CRC-16 (CCITT-FALSE) checksum at the end of the telemetry packet to verify data integrity upon reception.
* **Optional Display Output:** Supports U8g2-compatible monochrome displays to show real-time sensor data, GPS status, LoRa parameters, and PMU information, cycling through multiple screens.
* **Error Handling:** Includes basic error checks for sensor initialization failures and displays a fatal error message on the serial monitor and optionally on the display.

## Getting Started

### Prerequisites

* **Arduino IDE:** You will need the Arduino IDE installed on your computer.
* **Required Libraries:** Ensure you have the following libraries installed in your Arduino IDE. You can typically install these through the Arduino Library Manager (Sketch > Include Library > Manage Libraries...):
    * **RadioLib** by Jan Gromes ([https://github.com/jgromes/RadioLib](https://github.com/jgromes/RadioLib))
    * **Adafruit BME280 Library** by Adafruit ([https://github.com/adafruit/Adafruit_BME280_Library](https://github.com/adafruit/Adafruit_BME280_Library))
    * **Adafruit Unified Sensor Library** by Adafruit ([https://github.com/adafruit/Adafruit_Sensor](https://github.com/adafruit/Adafruit_Sensor))
    * **U8g2lib** by olikraus ([https://github.com/olikraus/u8g2](https://github.com/olikraus/u8g2))
    * **TinyGPS++** by Mikal Hart ([http://arduinogps.jjoe.org/](http://arduinogps.jjoe.org/))
* **Custom Libraries:**
    * **SensorQMC6310.hpp:** You will need to implement or obtain a library for the QMC6310 magnetometer.
    * **SensorQMI8658.hpp:** You will need to implement or obtain a library for the QMI8658 IMU.
    * **RS-FEC.h:** You will need to implement or obtain a Reed-Solomon Forward Error Correction library (e.g., [https://github.com/mersinvald/Reed-Solomon](https://github.com/mersinvald/Reed-Solomon)).
* **Hardware:**
    * An Arduino-compatible microcontroller (e.g., ESP32).
    * SX1262 LoRa transceiver module.
    * BME280 environmental sensor.
    * QMC6310 magnetometer.
    * QMI8658 IMU.
    * GPS module (with serial output).
    * Power Management Unit (PMU) integrated with your board (or accessible via I2C/other interface).
    * Optional: U8g2-compatible monochrome display.
    * Wires and breadboard for connections.

### Installation

1.  **Clone the Repository:** If you have the code in a repository, clone it to your local machine.
2.  **Install Libraries:** Use the Arduino Library Manager to install the required libraries mentioned in the Prerequisites.
3.  **Obtain Custom Libraries:** Place the `SensorQMC6310.hpp`, `SensorQMI8658.hpp`, and `RS-FEC.h` files (and their corresponding `.cpp` files if applicable) in the same directory as your `TelemetryTx.ino` sketch or in your Arduino libraries folder.
4.  **Configure `LoRaBoards.h`:** **This is a crucial step.** You will need to create or modify the `LoRaBoards.h` file (or a similar board-specific header file) to define the correct pin assignments for your specific hardware setup. This includes:
    * LoRa module SPI pins (CS, DIO1, RST, BUSY).
    * Optional: TCXO enable pin.
    * I2C pins (SDA, SCL) if they are non-standard for your board.
    * SPI instance for the QMI8658 (if shared with an SD card, define accordingly).
    * GPS serial port definition (`SerialGPS`, e.g., `Serial1`).
    * PMU object initialization and any necessary definitions to access the PMU.
    * Optional: Display connection details and the `U8G2_DISPLAY_SETUP` macro definition.

### Configuration

* **`LoRaBoards.h`:** As mentioned above, this file is critical for hardware-specific configurations. Ensure all pin definitions and the PMU object are correctly initialized for your board.
* **Compile-Time Constants:** Review the constants defined at the beginning of the `TelemetryTx.ino` file and adjust them as needed for your specific setup and region:
    * `SPACECRAFT_ID`: Set a unique identifier for your transmitter.
    * `CCSDS_APID`: You can change the Application Process Identifier if needed.
    * **LoRa Radio Configuration:** Adjust `LORA_CARRIER_FREQ`, `LORA_TX_POWER`, `LORA_BANDWIDTH`, `LORA_SPREADING_FACTOR`, `LORA_CODING_RATE`, and `LORA_SYNC_WORD` according to your LoRa network requirements and local regulations.
    * `BME280_SEALEVELPRESSURE_HPA`: Adjust this if you need more accurate altitude readings for your specific location.
    * `SENSOR_UPDATE_INTERVAL_MS`: Set the desired interval for reading sensor data.
    * `MAGNETIC_DECLINATION_DEGREES`: Update this value for your specific geographic location to improve the accuracy of the magnetic heading calculation. You can find this information at the provided link.
    * **Display Configuration:** Adjust `DISPLAY_DEFAULT_SCREEN_DELAY_MS`, `DISPLAY_GPS_SCREEN_DELAY_MS`, and `DISPLAY_NUM_SCREENS` if you are using a display and have modified the display drawing functions.
* **Sensor Libraries:** Ensure that the custom sensor libraries (`SensorQMC6310.hpp` and `SensorQMI8658.hpp`) are correctly implemented to communicate with your specific sensor modules.

## Usage

1.  **Connect Hardware:** Connect all the sensors, the LoRa module, the GPS module, and the optional display to your Arduino-compatible microcontroller according to the pin definitions in your `LoRaBoards.h` file.
2.  **Upload the Sketch:** Open the `TelemetryTx.ino` file in the Arduino IDE, select the correct board and port, and upload the sketch to your microcontroller.
3.  **Monitor Serial Output:** Open the Serial Monitor in the Arduino IDE (Tools > Serial Monitor) to observe the initialization process, any error messages, and basic telemetry information.
4.  **Observe Display (Optional):** If you have connected a display and configured it correctly, you should see real-time sensor data, GPS information, LoRa parameters, and PMU status cycling through different screens.
5.  **Receive Telemetry:** You will need a compatible LoRa receiver setup to receive and decode the telemetry data transmitted by this sketch. The receiver will need to implement the same LoRa parameters and the inverse process of Reed-Solomon decoding and CCSDS packet parsing to retrieve the original sensor data.

## CCSDS Packet Structure Notes

The telemetry data is structured into a packet format that resembles a CCSDS Application Packet (AP). Here's a breakdown of the header fields:

* **Packet Version Number (3 bits):** Set to `0b000` indicating CCSDS Version 1.
* **Type Indicator (1 bit):** Set to `0b0` indicating a Telemetry Packet.
* **Secondary Header Flag (1 bit):** Set to `0b1` indicating the presence of a secondary header (although in this simplified example, the secondary header is not explicitly populated beyond this flag).
* **APID (11 bits):** Set to `0x7FF` as an example Application Process Identifier. This can be changed if needed.
* **Sequence Flags (2 bits):** Set to `0b11` indicating a Standalone Packet, meaning each packet is self-contained.
* **Packet Length Field (14 bits):** Represents the length of the Packet Data Field minus one, calculated as `sizeof(CCSDSPacket) - 7`. This follows the CCSDS standard.

The Packet Data Field contains:

* Metadata: Spacecraft ID, Mission Time.
* Sensor Readings: Temperature, pressure, humidity, altitude (BME280); magnetic field (QMC6310); acceleration, gyroscope, temperature (QMI8658); GPS data; PMU data.
* Example Message Payload: A customizable string for status messages.
* CRC-16 Checksum: A 2-byte checksum calculated over the entire packet (excluding the checksum field itself) for data integrity.

## Reed-Solomon FEC Notes

This sketch implements a Reed-Solomon RS(255, 223) code for Forward Error Correction. This means:

* **223 Data Bytes:** The actual telemetry data (the `CCSDSPacket`) is treated as a block of up to 223 bytes. Since the `CCSDSPacket` structure is likely smaller than this, it is padded with zeros to reach the required message length before encoding.
* **32 Parity Bytes:** The RS encoder adds 32 parity bytes (error correction code) to the 223 data bytes.
* **255 Total Encoded Bytes:** The final transmitted block consists of 255 bytes (223 data + 32 parity).

The `CCSDSPacket` is copied into a 223-byte buffer (`rsPaddedMessage`), encoded using the Reed-Solomon library, and the resulting 255-byte encoded data (`rsEncodedData`) is transmitted via LoRa. The receiver will need to use a compatible RS(255, 223) decoder to correct any errors that might have occurred during transmission.

## Voyager Inspiration

While this project is a simplified implementation, it draws inspiration from deep space missions like Voyager 1:

* **Telemetry Transmission:** Spacecraft constantly transmit telemetry data back to Earth, providing crucial information about their health, status, and scientific observations.
* **Standardized Packet Formats:** Missions often rely on standardized packet formats like CCSDS to ensure interoperability and efficient data handling across different ground stations and systems.
* **Sensor Data:** Telemetry includes data from various sensors that monitor the spacecraft's environment, attitude, and the performance of its subsystems (similar to the sensors used in this project).
* **Forward Error Correction:** Due to the vast distances and challenging communication links in space, Forward Error Correction codes like Reed-Solomon are essential for ensuring reliable data transmission by adding redundancy that allows the receiver to detect and correct errors.

## Libraries Used

* **RadioLib:** For LoRa radio communication ([https://github.com/jgromes/RadioLib](https://github.com/jgromes/RadioLib))
* **LoRaBoards.h:** Board-specific definitions (pins, PMU object, etc.) - **Requires User Configuration**
* **Wire.h:** Standard Arduino library for I2C communication (BME280, QMC6310, potentially Display)
* **SPI.h:** Standard Arduino library for SPI communication (QMI8658, potentially Radio/SD)
* **Adafruit_Sensor.h & Adafruit_BME280.h:** For BME280 sensor ([https://github.com/adafruit/Adafruit_BME280_Library](https://github.com/adafruit/Adafruit_BME280_Library))
* **SensorQMC6310.hpp:** Custom sensor library - **Requires User Implementation/Source**
* **SensorQMI8658.hpp:** Custom sensor library - **Requires User Implementation/Source**
* **U8g2lib.h:** For U8g2 monochrome display library ([https://github.com/olikraus/u8g2](https://github.com/olikraus/u8g2))
* **math.h:** Standard C math library
* **RS-FEC.h:** Reed-Solomon library - **Requires User Implementation/Source** (e.g., [https://github.com/mersinvald/Reed-Solomon](https://github.com/mersinvald/Reed-Solomon))
* **TinyGPS++.h:** For GPS NMEA sentence parsing ([http://arduinogps.jjoe.org/](http://arduinogps.jjoe.org/))
* **stdio.h:** Standard C input/output library (for `snprintf`)

## Hardware Assumptions

This sketch assumes the following hardware connections:

* **Microcontroller:** Arduino-compatible board with sufficient resources.
* **LoRa Transceiver:** SX1262 module connected via SPI. The specific pins (CS, DIO1, RST, BUSY) must be defined correctly in `LoRaBoards.h`.
* **BME280:** Connected via I2C. Assumes the default I2C address (0x76 or 0x77).
* **QMC6310:** Connected via I2C. The I2C address is configurable in the code (`QMC6310_SLAVE_ADDRESS`). Ensure the correct SDA and SCL pins are used in `qmc.begin()`.
* **QMI8658:** Connected via SPI. The Chip Select (CS) pin must be defined as `IMU_CS` in `LoRaBoards.h`. The SPI instance might be `SPI` or a different instance like `SDCardSPI` depending on your board.
* **GPS Module:** Connected to a dedicated serial port (defined as `SerialGPS` in the code, likely needs to be configured in `LoRaBoards.h` or the main sketch). The baud rate is set to 9600.
* **PMU:** Accessible via a global object named `PMU`. The definition and initialization of this object are expected to be handled in `LoRaBoards.h` based on your specific board's PMU.
* **Display (Optional):** A U8g2-compatible monochrome display connected via I2C or another supported interface. The `U8G2_DISPLAY_SETUP` macro in `LoRaBoards.h` controls whether the display functionality is enabled.

## Configuration

The most important configuration steps involve:

1.  **`LoRaBoards.h`:** Carefully define all the pin numbers and the PMU object according to your specific hardware. This file acts as a board support package.
2.  **Custom Sensor Libraries:** Ensure that you have correctly implemented or obtained the `SensorQMC6310.hpp` and `SensorQMI8658.hpp` libraries so that the `qmc` and `qmi` objects can communicate with your magnetometer and IMU sensors. The placeholder implementations in the code need to be replaced with actual sensor communication logic. Similarly, ensure the `RS-FEC.h` library is correctly integrated.
3.  **LoRa Parameters:** Review and adjust the LoRa communication parameters (frequency, power, bandwidth, spreading factor, coding rate, sync word) to match your intended LoRa network.
4.  **Magnetic Declination:** Update the `MAGNETIC_DECLINATION_DEGREES` constant with the correct value for your location to improve the accuracy of the calculated magnetic heading.

## Error Handling

The sketch includes basic error handling for sensor initialization. If the BME280, QMC6310, or QMI8658 sensors fail to initialize, a fatal error message will be printed to the Serial Monitor, and optionally displayed on the U8g2 display. The program will then enter an infinite loop, halting further execution.

## Display Functionality

If a U8g2-compatible display is configured (by defining `U8G2_DISPLAY_SETUP` in `LoRaBoards.h`), the sketch will cycle through multiple screens displaying:

* Real-time sensor readings (temperature, pressure, humidity, altitude).
* Magnetometer data and calculated heading.
* IMU data (acceleration, gyroscope, temperature).
* GPS status (number of satellites, HDOP).
* GPS location (latitude, longitude, altitude).
* GPS date and time.
* LoRa configuration parameters.
* PMU status (battery voltage, percentage, charging status, VBUS voltage, system voltage).

The delay between screen switches can be configured using `DISPLAY_DEFAULT_SCREEN_DELAY_MS` and `DISPLAY_GPS_SCREEN_DELAY_MS`.

## Contributing

Contributions to this project are welcome. Feel free to submit pull requests or open issues for bug fixes, feature requests, or improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

* The RadioLib library for providing a great interface to LoRa hardware.
* The Adafruit BME280 library for easy interaction with the environmental sensor.
* The U8g2 library for its excellent support for monochrome displays.
* The TinyGPS++ library for making GPS data parsing straightforward.
* Inspiration from the engineering teams behind the Voyager missions for their pioneering work in space communication.

---

