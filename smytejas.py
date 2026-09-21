from  cable_sizing import *
import sys 




def main():
    choice =  int(input("Choose option\n1. Cable Sizing\n2. Lighting\n3. Exit "))
    
    if choice == 1:
        Cable_sizing().cable_size()
        
    elif choice ==  2:
        sys.exit()
    else:
        sys.exit()
        

if __name__ == "__main__":
    main()
    