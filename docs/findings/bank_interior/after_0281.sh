cd /c/Projects/gabagool_studios/gabagool_factory || exit 9
[ "$(cat deli_counter/VERSION)" = "Deli Counter 0.281.0" ] || { echo "DELI COUNTER IS NOT 0.281.0"; exit 1; }
WS=workspaces/bank-look-0281-ws
[ ! -e $WS ] || { echo "$WS EXISTS"; exit 1; }
( time .venv/Scripts/python.exe -m level_factory -C $WS make _scratch/bank_look_input/batch.json --seed 9082 ) > _scratch/bank_0281_make.log 2>&1; echo "make=$?"; tail -4 _scratch/bank_0281_make.log
bash _scratch/bank_0281_shoot.sh
python docs/findings/bank_interior/price_0281.py > docs/findings/bank_interior/price_0281.out.txt 2>&1; echo "price=$?"
