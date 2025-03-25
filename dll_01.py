import ctypes

# --- Configuration ---
dll_path = "/home/mobase/Sagar/dll/VT_AY_BCM_CANoe_Config_R1.cfg_networks.dll"  # Replace with the actual DLL path
seed_value = (0xff, 0xfe, 0xfd, 0xfc)  # Example seed value from ECU
security_level = 1  # Example security level (if applicable)
# --- End Configuration ---

# 1. Load the DLL
try:
    mylib = ctypes.WinDLL(dll_path)
except OSError as e:
    print(f"Error loading DLL: {e}")
    exit()

# 2. Define data types for DLL functions
c_byte = ctypes.c_ubyte
c_short = ctypes.c_ushort
c_int = ctypes.c_int
c_void_p = ctypes.c_void_p

# 3. Define the DLL function signature (Example: GenerateKeyEx)
mylib.GenerateKeyEx.argtypes = [
    ctypes.POINTER(c_byte),  # Seed (pointer to byte array)
    c_int,  # Seed length
    c_int,  # Security level (if applicable)
    c_void_p,  # Options (NULL if not used)
    ctypes.POINTER(c_byte),  # Key (pointer to byte array)
    c_int,  # Max key length
    ctypes.POINTER(c_int),  # Actual key length
]
mylib.GenerateKeyEx.restype = ctypes.c_int  # Return code (e.g., 0 for success)

# 4. Prepare the seed and key buffers
seed = (c_byte * len(seed_value))(*seed_value)
key = (c_byte * 8)()  # Allocate space for the key (8 bytes is a common size)
key_length = c_int(0)

# 5. Call the DLL function
try:
    result = mylib.GenerateKeyEx(
        ctypes.byref(seed),
        len(seed_value),
        security_level,
        None,  # Options (NULL if not used)
        ctypes.byref(key),
        8,  # Max key length
        ctypes.byref(key_length)
    )

    if result == 0:
        print("Key generated successfully!")
        print("Key:", bytes(key[:key_length.value]))
    else:
        print(f"Error generating key: {result}")
except Exception as e:
    print(f"Error during DLL call: {e}")
