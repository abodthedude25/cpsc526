echo "Enter file suffix number"
read file
echo "Running 'python3 fw.py rules${file}.txt packets${file}.txt | diff -y results${file}.txt - '"
python3 fw.py rules${file}.txt packets${file}.txt | diff -y results${file}.txt - 
if python3 fw.py rules${file}.txt packets${file}.txt | cmp -s results${file}.txt -; then
 echo "results match"
else 
 echo "results differ"
fi
