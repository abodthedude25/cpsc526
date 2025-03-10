#!/bin/bash

# Function to run Task 1 test cases
run_task1_tests() {
    echo "Running Task 1 Test Cases"
    echo "========================="
    
    # Test Case 1: Basic Text File Decryption
    echo -e "\nTest Case 1: Basic Text File Decryption"
    echo "----------------------------------------"
    echo -e "Encrypting sample1.txt...\n"
    echo "./enkrypt.py cpsc526 < inp/sample1.txt > out/sample1.txt.enc"
    ./enkrypt.py cpsc526 < inp/sample1.txt > out/sample1.txt.enc
    echo -e "Decrypting sample1.txt.enc...\n"
    echo "./dekrypt1.py cpsc526 < out/sample1.txt.enc"
    ./dekrypt1.py cpsc526 < out/sample1.txt.enc
    echo -e "\nExpected Output: What is the answer to life, universe and everything?"
    
    # Test Case 2: Binary File Decryption
    echo -e "\nTest Case 2: Binary File Decryption"
    echo "--------------------------------------"
    echo -e "Encrypting tower.png...\n"
    echo "./enkrypt.py YYC < inp/tower.png > out/tower.png.enc"
    ./enkrypt.py YYC < inp/tower.png > out/tower.png.enc
    echo -e "Decrypting tower.png.enc...\n"
    echo "./dekrypt1.py YYC < out/tower.png.enc > out/decrypted_tower.png"
    ./dekrypt1.py YYC < out/tower.png.enc > out/decrypted_tower.png
    echo -e "Checking SHA256 hash...\n"
    echo "sha256sum inp/tower.png out/decrypted_tower.png"
    sha256sum inp/tower.png out/decrypted_tower.png
    
    # Test Case 3: Incorrect Password
    echo -e "\nTest Case 3: Incorrect Password"
    echo "----------------------------------"
    echo -e "Decrypting sample1.txt.enc with wrong password...\n"
    echo "./dekrypt1.py wrongpass < out/sample1.txt.enc"
    ./dekrypt1.py wrongpass < out/sample1.txt.enc
    echo -e "\nExpected Output: Garbage data (different from original)"
    
    # Test Case 4: Empty File
    echo -e "\nTest Case 4: Empty File"
    echo "-------------------------"
    echo -e "Creating empty.txt...\n"
    echo "touch empty.txt"
    touch empty.txt
    echo -e "Encrypting empty.txt...\n"
    echo "./enkrypt.py cpsc526 < empty.txt > out/empty.txt.enc"
    ./enkrypt.py cpsc526 < empty.txt > out/empty.txt.enc
    echo -e "Decrypting empty.txt.enc...\n"
    echo "./dekrypt1.py cpsc526 < out/empty.txt.enc > out/decrypted_empty.txt"
    ./dekrypt1.py cpsc526 < out/empty.txt.enc > out/decrypted_empty.txt
    echo -e "Listing decrypted file...\n"
    echo "ls -l out/decrypted_empty.txt"
    ls -l out/decrypted_empty.txt
    
    # Test Case 5: Large File
    echo -e "\nTest Case 5: Large File"
    echo "-------------------------"
    echo -e "Creating large_file.bin...\n"
    echo "dd if=/dev/urandom of=large_file.bin bs=1M count=10"
    dd if=/dev/urandom of=large_file.bin bs=1M count=10
    echo -e "Encrypting large_file.bin...\n"
    echo "./enkrypt.py mypassword < large_file.bin > out/large_file.bin.enc"
    ./enkrypt.py mypassword < large_file.bin > out/large_file.bin.enc
    echo -e "Decrypting large_file.bin.enc...\n"
    echo "./dekrypt1.py mypassword < out/large_file.bin.enc > out/decrypted_large_file.bin"
    ./dekrypt1.py mypassword < out/large_file.bin.enc > out/decrypted_large_file.bin
    echo -e "Checking SHA256 hash...\n"
    echo "sha256sum large_file.bin out/decrypted_large_file.bin"
    sha256sum large_file.bin out/decrypted_large_file.bin
    
    # Test Case 6: Short Message
    echo -e "\nTest Case 6: Short Message"
    echo "---------------------------"
    echo -e "Encrypting short message...\n"
    echo "echo \"hello world\" | ./enkrypt.py YYC > out/short_message.enc"
    echo "hello world" | ./enkrypt.py YYC > out/short_message.enc
    echo -e "Decrypting short_message.enc...\n"
    echo "./dekrypt1.py YYC < out/short_message.enc"
    ./dekrypt1.py YYC < out/short_message.enc
}

# Function to run Task 2 test cases
run_task2_tests() {
    echo "Running Task 2 Test Cases"
    echo "========================="
    
    # Test Case 1: Non-trivial password guess
    echo -e "\nTest Case 1: Non-trivial password guess"
    echo "-----------------------------------------"
    echo -e "Encrypting sample1.txt with password 'cpsc526'...\n"
    echo "./enkrypt.py cpsc526 < inp/sample1.txt > out/sample1.txt.enc"
    ./enkrypt.py cpsc526 < inp/sample1.txt > out/sample1.txt.enc
    echo -e "Running dekrypt2.py with pattern 'cpsc52_'...\n"
    echo "./dekrypt2.py cpsc52_ < out/sample1.txt.enc"
    ./dekrypt2.py cpsc52_ < out/sample1.txt.enc
    
    # Test Case 2: One underscore at the end
    echo -e "\nTest Case 2: One underscore at the end"
    echo "----------------------------------------"
    echo -e "Encrypting sample1.txt with password 'cpsc5263'...\n"
    echo "./enkrypt.py cpsc5263 < inp/sample1.txt > out/sample1_1.txt.enc"
    ./enkrypt.py cpsc5263 < inp/sample1.txt > out/sample1_1.txt.enc
    echo -e "Running dekrypt2.py with pattern 'cpsc526_'...\n"
    echo "./dekrypt2.py cpsc526_ < out/sample1_1.txt.enc"
    ./dekrypt2.py cpsc526_ < out/sample1_1.txt.enc
    
    # Test Case 3: 2-6 underscores at the end
    echo -e "\nTest Case 3: 2-6 underscores at the end"
    echo "-----------------------------------------"
    echo -e "Testing with 2 underscores...\n"
    echo -e "Encrypting sample1.txt with password 'cpsc00'...\n"
    echo "./enkrypt.py cpsc00 < inp/sample1.txt > out/sample1_2.txt.enc"
    ./enkrypt.py cpsc00 < inp/sample1.txt > out/sample1_2.txt.enc
    echo -e "Running dekrypt2.py with pattern 'cpsc__'...\n"
    echo "./dekrypt2.py cpsc__ < out/sample1_2.txt.enc"
    ./dekrypt2.py cpsc__ < out/sample1_2.txt.enc
    
    echo -e "\nTesting with 3 underscores...\n"
    echo -e "Encrypting sample1.txt with password 'cpsc123'...\n"
    echo "./enkrypt.py cpsc123 < inp/sample1.txt > out/sample1_3.txt.enc"
    ./enkrypt.py cpsc123 < inp/sample1.txt > out/sample1_3.txt.enc
    echo -e "Running dekrypt2.py with pattern 'cpsc___'...\n"
    echo "./dekrypt2.py cpsc___ < out/sample1_3.txt.enc"
    ./dekrypt2.py cpsc___ < out/sample1_3.txt.enc
    
    echo -e "\nTesting with 4 underscores...\n"
    echo -e "Encrypting sample1.txt with password 'cpsc4567'...\n"
    echo "./enkrypt.py cpsc4567 < inp/sample1.txt > out/sample1_4.txt.enc"
    ./enkrypt.py cpsc4567 < inp/sample1.txt > out/sample1_4.txt.enc
    echo -e "Running dekrypt2.py with pattern 'cpsc____'...\n"
    echo "./dekrypt2.py cpsc____ < out/sample1_4.txt.enc"
    ./dekrypt2.py cpsc____ < out/sample1_4.txt.enc
    
    echo -e "\nTesting with 5 underscores...\n"
    echo -e "Encrypting sample1.txt with password 'cpsc89012'...\n"
    echo "./enkrypt.py cpsc89012 < inp/sample1.txt > out/sample1_5.txt.enc"
    ./enkrypt.py cpsc89012 < inp/sample1.txt > out/sample1_5.txt.enc
    echo -e "Running dekrypt2.py with pattern 'cpsc_____'...\n"
    echo "./dekrypt2.py cpsc_____ < out/sample1_5.txt.enc"
    ./dekrypt2.py cpsc_____ < out/sample1_5.txt.enc
    
    echo -e "\nTesting with 6 underscores...\n"
    echo -e "Encrypting sample1.txt with password 'cpsc345678'...\n"
    echo "./enkrypt.py cpsc345678 < inp/sample1.txt > out/sample1_6.txt.enc"
    ./enkrypt.py cpsc345678 < inp/sample1.txt > out/sample1_6.txt.enc
    echo -e "Running dekrypt2.py with pattern 'cpsc______'...\n"
    echo "./dekrypt2.py cpsc______ < out/sample1_6.txt.enc"
    time ./dekrypt2.py cpsc______ < out/sample1_6.txt.enc

    
    # Test Case 5: Duplicate passwords
    echo -e "\nTest Case 5: Duplicate passwords"
    echo "-----------------------------------"
    echo -e "Encrypting sample1.txt with password 'aaaa'...\n"
    echo "./enkrypt.py aaaa < inp/sample1.txt > out/sample1_8.txt.enc"
    ./enkrypt.py aaaa < inp/sample1.txt > out/sample1_8.txt.enc
    echo -e "Running dekrypt2.py with pattern 'a_a'...\n"
    echo "./dekrypt2.py a_a < out/sample1_8.txt.enc"
    ./dekrypt2.py a_a < out/sample1_8.txt.enc
    
    # Test Case 6: Patterns without underscores
    echo -e "\nTest Case 6: Patterns without underscores"
    echo "-------------------------------------------"
    echo -e "Encrypting sample1.txt with password 'cpsc526'...\n"
    echo "./enkrypt.py cpsc526 < inp/sample1.txt > out/sample1_9.txt.enc"
    ./enkrypt.py cpsc526 < inp/sample1.txt > out/sample1_9.txt.enc
    echo -e "Running dekrypt2.py with pattern 'cpsc526'...\n"
    echo "./dekrypt2.py cpsc526 < out/sample1_9.txt.enc"
    ./dekrypt2.py cpsc526 < out/sample1_9.txt.enc
}

# Function to run Task 3 test cases
run_task3_tests() {
    echo "Running Task 3 Test Cases"
    echo "========================="
    
    # Test Case 1: Successful Decryption with Reused Nonces
    echo -e "\nTest Case 1: Successful Decryption with Reused Nonces"
    echo "------------------------------------------------------"
    echo -e "Encrypting 1984.txt with nonce 123...\n"
    echo "./enkrypt.py -nonce 123 unknown < inp/1984.txt > out/1984.txt.enc"
    ./enkrypt.py -nonce 123 unknown < inp/1984.txt > out/1984.txt.enc
    echo -e "Encrypting secret.txt with nonce 123...\n"
    echo "./enkrypt.py -nonce 123 unknown < inp/secret.txt > out/secret.txt.enc"
    ./enkrypt.py -nonce 123 unknown < inp/secret.txt > out/secret.txt.enc
    echo -e "Running dekrypt3.py...\n"
    echo "./dekrypt3.py inp/1984.txt out/1984.txt.enc out/secret.txt.enc > out/recovered_secret.txt"
    ./dekrypt3.py inp/1984.txt out/1984.txt.enc out/secret.txt.enc > out/recovered_secret.txt
    echo -e "Checking if recovered file matches original...\n"
    echo "diff inp/secret.txt out/recovered_secret.txt"
    diff inp/secret.txt out/recovered_secret.txt
    
    # Test Case 2: Decryption Failure with Different Nonces
    echo -e "\nTest Case 2: Decryption Failure with Different Nonces"
    echo "------------------------------------------------------"
    echo -e "Encrypting 1984.txt with nonce 123...\n"
    echo "./enkrypt.py -nonce 123 unknown < inp/1984.txt > out/1984.txt.enc"
    ./enkrypt.py -nonce 123 unknown < inp/1984.txt > out/1984.txt.enc
    echo -e "Encrypting sample1.txt with nonce 456...\n"
    echo "./enkrypt.py -nonce 456 unknown < inp/sample1.txt > out/sample1.txt.enc"
    ./enkrypt.py -nonce 456 unknown < inp/sample1.txt > out/sample1.txt.enc
    echo -e "Running dekrypt3.py...\n"
    echo "./dekrypt3.py inp/1984.txt out/1984.txt.enc out/sample1.txt.enc"
    ./dekrypt3.py inp/1984.txt out/1984.txt.enc out/sample1.txt.enc
    
    # Test Case 3: Decryption with Binary Files
    echo -e "\nTest Case 3: Decryption with Binary Files"
    echo "-------------------------------------------"
    echo -e "Encrypting tower.png with nonce 789...\n"
    echo "./enkrypt.py -nonce 789 unknown < inp/tower.png > out/tower.png.enc"
    ./enkrypt.py -nonce 789 unknown < inp/tower.png > out/tower.png.enc
    echo -e "Encrypting secret.txt with nonce 789...\n"
    echo "./enkrypt.py -nonce 789 unknown < inp/secret.txt > out/secret.txt.enc"
    ./enkrypt.py -nonce 789 unknown < inp/secret.txt > out/secret.txt.enc
    echo -e "Running dekrypt3.py...\n"
    echo "./dekrypt3.py inp/tower.png out/tower.png.enc out/secret.txt.enc > out/recovered_secret.txt"
    ./dekrypt3.py inp/tower.png out/tower.png.enc out/secret.txt.enc > out/recovered_secret.txt
    echo -e "Checking if recovered file matches original...\n"
    echo "diff inp/secret.txt out/recovered_secret.txt"
    diff inp/secret.txt out/recovered_secret.txt
    
    # Test Case 4: Decryption with Partial Overlap
    echo -e "\nTest Case 4: Decryption with Partial Overlap"
    echo "---------------------------------------------"
    echo -e "Creating shorter version of 1984.txt...\n"
    echo "head -n 10 inp/1984.txt > inp/short_1984.txt"
    head -n 10 inp/1984.txt > inp/short_1984.txt
    echo -e "Encrypting short_1984.txt with nonce 123...\n"
    echo "./enkrypt.py -nonce 123 unknown < inp/short_1984.txt > out/short_1984.txt.enc"
    ./enkrypt.py -nonce 123 unknown < inp/short_1984.txt > out/short_1984.txt.enc
    echo -e "Encrypting full 1984.txt with nonce 123...\n"
    echo "./enkrypt.py -nonce 123 unknown < inp/1984.txt > out/full_1984.txt.enc"
    ./enkrypt.py -nonce 123 unknown < inp/1984.txt > out/full_1984.txt.enc
    echo -e "Running dekrypt3.py...\n"
    echo "./dekrypt3.py inp/short_1984.txt out/short_1984.txt.enc out/full_1984.txt.enc > out/recovered_1984.txt"
    ./dekrypt3.py inp/short_1984.txt out/short_1984.txt.enc out/full_1984.txt.enc > out/recovered_1984.txt
    echo -e "Checking if recovered portion matches...\n"
    echo "diff inp/short_1984.txt out/recovered_1984.txt"
    diff inp/short_1984.txt out/recovered_1984.txt
    
    # Test Case 5: Decryption with Empty File
    echo -e "\nTest Case 5: Decryption with Empty File"
    echo "-----------------------------------------"
    echo -e "Creating empty.txt...\n"
    echo "touch inp/empty.txt"
    touch inp/empty.txt
    echo -e "Encrypting empty.txt with nonce 123...\n"
    echo "./enkrypt.py -nonce 123 unknown < inp/empty.txt > out/empty.txt.enc"
    ./enkrypt.py -nonce 123 unknown < inp/empty.txt > out/empty.txt.enc
    echo -e "Encrypting secret.txt with nonce 123...\n"
    echo "./enkrypt.py -nonce 123 unknown < inp/secret.txt > out/secret.txt.enc"
    ./enkrypt.py -nonce 123 unknown < inp/secret.txt > out/secret.txt.enc
    echo -e "Running dekrypt3.py...\n"
    echo "./dekrypt3.py inp/empty.txt out/empty.txt.enc out/secret.txt.enc > out/recovered_secret.txt"
    ./dekrypt3.py inp/empty.txt out/empty.txt.enc out/secret.txt.enc > out/recovered_secret.txt
    echo -e "Checking if recovered file matches original...\n"
    echo "diff inp/secret.txt out/recovered_secret.txt"
    diff inp/secret.txt out/recovered_secret.txt
    
    # Test Case 6: Decryption with Non-text Files
    echo -e "\nTest Case 6: Decryption with Non-text Files"
    echo "--------------------------------------------"
    echo -e "Encrypting tower.png with nonce 123...\n"
    echo "./enkrypt.py -nonce 123 unknown < inp/tower.png > out/tower1.png.enc"
    ./enkrypt.py -nonce 123 unknown < inp/tower.png > out/tower1.png.enc
    echo -e "Encrypting tower.png again with nonce 123...\n"
    echo "./enkrypt.py -nonce 123 unknown < inp/tower.png > out/tower2.png.enc"
    ./enkrypt.py -nonce 123 unknown < inp/tower.png > out/tower2.png.enc
    echo -e "Running dekrypt3.py...\n"
    echo "./dekrypt3.py inp/tower.png out/tower1.png.enc out/tower2.png.enc"
    ./dekrypt3.py inp/tower.png out/tower1.png.enc out/tower2.png.enc
}

# Main script
if [ $# -eq 0 ]; then
    echo "Usage: $0 <task_number>"
    echo "Where <task_number> is 1, 2, or 3"
    exit 1
fi

task=$1

case $task in
    1)
        run_task1_tests
        ;;
    2)
        run_task2_tests
        ;;
    3)
        run_task3_tests
        ;;
    4)
        rm -rf out/*
        ;;
    *)
        echo "Invalid task number. Please use 1, 2, or 3."
        exit 1
        ;;
esac
