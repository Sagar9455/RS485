def g():
variable=0
varFinal=0
try:
    while True:
        if GPIO.input(BTN_FIRST) == GPIO.LOW:
            variable=(variable*10)+1
            selected_sequence.append(BTN_FIRST)
            b = str(variable)
            display_text(b)
            #time.sleep(0.2)

        if GPIO.input(BTN_SECOND) == GPIO.LOW:
            variable=(variable*10)+2
            selected_sequence.append(BTN_SECOND)
            a = str(variable)
            display_text(a)
            #time.sleep(0.2)      

        if GPIO.input(BTN_ENTER) == GPIO.LOW:
            varFinal=variable
            variable=0
            selected_sequence.append(BTN_ENTER)
                
            selected_option = menu_combinations.get(tuple(selected_sequence), "Invalid Input")
            display_text(f"{selected_option}")

            if selected_option == "ECU Information":
                time.sleep(0.5)
                display_text("Fetching\nECU Information...")
                get_ecu_information()
                display_text("Completed")
           # if selected_option == "Testcase Execution":
               # time.sleep(0.5)
            #    display_text("Sahithi is working...")
                #get_ecu_information()
                #display_text("Completed")
            if selected_option == "Exit":
                os.system("exit")
            selected_sequence.clear()  # Reset sequence after confirmation
            #time.sleep(0.1)

        if GPIO.input(BTN_THANKS) == GPIO.LOW:
            display_text("Shutting Down")
            time.sleep(0.1)
            os.system('sudo poweroff')

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    GPIO.cleanup()
