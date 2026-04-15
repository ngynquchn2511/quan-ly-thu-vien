"""
ENTRY POINT CHINH
Chay admin: python main.py admin
Chay user:  python main.py user
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if len(sys.argv) < 2 or sys.argv[1] not in ["admin", "user"]:
    print("Dung: python main.py [admin|user]")
    sys.exit(1)

if sys.argv[1] == "admin":
    from admin_app.main import main
else:
    from user_app.main import main

main()
