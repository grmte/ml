import os
import commands

desired_statistic_line_numbers = [6,9,15]    # Line numbers for desired statistics
desired_statistic_names = ["Feature Combination","EntryCL","ExitCL","Total Sell Qty","Total Buy Qty", "Average Gross"]
#os.chdir("")    # Directory name needed
summary_file_name = "Accumulated_Results.csv"
print "\nOpening Trade Result file : ", summary_file_name
print "\nStatistics to summarize are : "

for statistic in desired_statistic_names:
    print statistic

write_file_object = open(summary_file_name, 'w')
command_output = commands.getoutput("ls -1")
file_list = command_output.split("\n")

filtered_file_list = [file_name for file_name in file_list if file_name[-6:] == ".trade"]

for name in desired_statistic_names:
    write_file_object.write(name + ";")

write_file_object.write("\n")    # Header done

for file_name in filtered_file_list:
    
    feature = file_name[:file_name.index("g")]
    write_file_object.write(feature + ";")
    entryCL = file_name[file_name.index("."):file_name.index("-")]
    write_file_object.write(entryCL + ";")
    exitCL = file_name[file_name.index("-")+1:file_name.rindex(".")]
    write_file_object.write(exitCL + ";")
    temp_read_file_object = open(file_name, "r")
    line_list = temp_read_file_object.readlines()
    
    for index in desired_statistic_line_numbers:
        
        last_occurence_of_space = line_list[index].rindex(" ")
        statistic = line_list[index][last_occurence_of_space + 1:-1]
        write_file_object.write(str(statistic) + ";")
    
    write_file_object.write("\n")

print "\nAll the files are summarized according to the statistic parameters given"
