//Notes: Log window will save after each new image is processed. It is saved with a timestamp. If at the end of a session
//you didn't make any mistakes like closing the 'Results' window, just keep the most recent file created. Otherwise you can
//create a fixed file containing the results before the window was closed. 


//This is the only line of code you modify. End path in a forward slash /
home = "C:/Users/Acer/Desktop/check if working/test/"


/////////////////////////////////////////////////////////////////////////////////////////////////
roi_folder = home + "ROIs"
results_folder = home + "Excel Sheets/IJ Polygon Logs/"

title = getTitle();
title_ne = File.nameWithoutExtension;

run("Set Measurements...", "area mean standard modal min centroid center perimeter bounding fit shape feret's integrated median skewness kurtosis area_fraction stack limit display redirect=None decimal=3");
run("Split Channels");

//Prepare the V5 channel
run("Z Project...", "projection=[Standard Deviation]");
selectWindow("C3-" + title);
close();
selectWindow("STD_C3-" + title);
run("Green");
run("Enhance Contrast", "saturated=0.35");
run("Duplicate...", " ");  // as reference image later
rename("Stacked");

//Prepare the GFAP channel
selectWindow("C2-" + title);
run("Z Project...", "projection=[Standard Deviation]");
selectWindow("C2-" + title);
close();
selectWindow("STD_C2-" + title);
run("Red");

//Prepare the IB4 Channel
selectWindow("C1-" + title);
run("Z Project...", "projection=[Standard Deviation]");
selectWindow("C1-" + title);
close();
run("Enhance Contrast", "saturated=0.35");
run("Red");


//Threshold V5 Channel
//Make 2 copies. One for outline and one for holes
selectWindow("STD_C3-" + title);
setOption("ScaleConversions", true);
run("8-bit");

//Ask User Which Threshold is Best
run("Auto Threshold", "method=[Try all] white");
choice = getNumber("prompt", 1);

if (choice == 1){
	close(); // closes tiled window
	run("Auto Threshold", "method=Huang white");
	run("Duplicate...", " ");
}else{
	close();  // closes tiled window
	run("Auto Threshold", "method=Default white");
	run("Duplicate...", " ");
}

//Remove outer edges' one pixel so Analyze particles doesnt get confused

//normal binary
height = getHeight();
width = getWidth();
makeRectangle(0, 0, 1, height);
run("Set...", "value=0");
makeRectangle(0, 0, width, 1);
run("Set...", "value=0");
makeRectangle(width-1, 0, 1, height);
run("Set...", "value=0");
makeRectangle(0, height-1, width, 1);
run("Set...", "value=0");
run("Select None");

run("Duplicate...", " ");
selectWindow("STD_C3-" + title);
close();

//Because of the way ImageJ names windows, 1.nd2 and 2.nd2 get problematic window naming. The if, else if, else blocks fix this
//if (title_ne == "1"){
//	selectWindow("STD_C3-3.nd2");
//}else if (title_ne == "2"){
//	selectWindow("STD_C3-3.nd2");
//}else{
//	selectWindow("STD_C3-2.nd2");
//}
selectWindow("STD_C3-" + title_ne + "-2.nd2");


run("Analyze Particles...", "size=3-Infinity exclude add");
roiManager("Show None");

//inverted binary
//if (title_ne == "1"){
//	selectWindow("STD_C3-2.nd2"); //changed +1*
//}else{
//	selectWindow("STD_C3-1.nd2");
//}

selectWindow("STD_C3-" + title_ne + "-1.nd2");
run("Invert");
run("Grays");

//Remove outer edges' one pixel so Analyze particles doesnt get confused
makeRectangle(0, 0, 1, height);
run("Set...", "value=255");
makeRectangle(0, 0, width, 1);
run("Set...", "value=255");
makeRectangle(width-1, 0, 1, height);
run("Set...", "value=255");
makeRectangle(0, height-1, width, 1);
run("Set...", "value=255");
run("Select None");

run("Duplicate...", " ");
//Because of the way ImageJ names windows, 1.nd2 and 2.nd2 get problematic window naming. The if, else if, else blocks fix this
//if (title_ne == "1"){
//	selectWindow("STD_C3-2.nd2"); //changed +1*
//	close();
//	selectWindow("STD_C3-1.nd2"); //changed *
//}else if (title_ne == "2"){
//	selectWindow("STD_C3-1.nd2"); //changed +1*
//	close();
//	selectWindow("STD_C3-2.nd2"); //changed *
//}else{
//	selectWindow("STD_C3-1.nd2");
//	close();
//	selectWindow("STD_C3-3.nd2");
//}
selectWindow("STD_C3-" + title_ne + "-1.nd2");
close();
selectWindow("STD_C3-" + title_ne + "-3.nd2");

run("Analyze Particles...", "size=3-Infinity exclude add");
selectWindow("Stacked");
selectWindow("ROI Manager");
waitForUser("Take Care of V5 ROIs");
close();
close();

//Threshold GFAP
selectWindow("STD_C2-" + title);
setOption("ScaleConversions", true);
run("8-bit");
run("Auto Local Threshold", "method=Phansalkar radius=15 parameter_1=0 parameter_2=0 white");
run("Grays");

//Measure GFAP Using ROI; Save ROI
selectWindow("STD_C2-" + title);
run("Grays");
roiManager("Select", 0);
roiManager("Rename", "full_outline");
run("Measure");
roiManager("Save", roi_folder + "/Full Complex/full_outline_" + title + ".roi");

//Make Convex Hull Selection of Outline, Measure, and Save ROI
run("Convex Hull");
roiManager("Add");
roiManager("Select", 1);
roiManager("Rename", "convex_hull");
run("Measure");
roiManager("Save", roi_folder + "/Convex Hull/convex_hull_" + title + ".roi");

//Set up Pause State
roiManager("Select", 0);
waitForUser("Check Everything Looks Good");

//Clean Up to Start Next Image
getDateAndTime(year, month, dayOfWeek, dayOfMonth, hour, minute, second, msec);
MonthNames = newArray("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec");
m = MonthNames[month];
saveAs("Results", results_folder + "Results_" + m + "_" + dayOfMonth + "_" + year + "-" + hour + ";" + minute + "," + second + msec +  ".csv");

roiManager("Deselect");
roiManager("Delete");

close();
close();
close();
