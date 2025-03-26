from datetime import datetime
now = datetime.now()
def create_asc_file(file_name):
	ctime = now.strftime("%M.%s")
	can_data = [
	(now.strftime("%M.%s"), "TX", 0x104, 8, [0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07]),
	(now.strftime("%M.%s"), "RX", 0x101, 4, [0x01, 0x11, 0x22, 0x33, 0x04, 0x05, 0x06, 0x07]),
	(now.strftime("%M.%s"), "TX", 0x106, 8, [0x22, 0x41, 0x02, 0x43, 0x2, 0x15, 0x26, 0x77]),
	]

	with open('Rasp_can_log3.asc', 'w') as file:
		file.write('Timestamp   Direction	Msg_ID	DLC  data\n')
		for frame in can_data:
			Timestamp = frame[0]
			Direction = frame[1]
			Msg_ID = frame[2]
			DLC =  frame[3]
			data = frame[4]
			
			data_str = ' '.join([f"{byte:02X}" for byte in data])
			file.write(f"{Timestamp}     {Direction}          {Msg_ID:03X}     {DLC}    {data_str}\n")
		
create_asc_file("Rasp_can_log99.asc")
 
