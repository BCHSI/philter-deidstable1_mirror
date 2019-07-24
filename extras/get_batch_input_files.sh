#!/usr/bin/csh
foreach dir (`find $1 -mindepth $3 -maxdepth $3 -name "*"`)
   	set var1="`echo $dir| cut -f 5- -d /`"
	echo $var1
        set var2 = $2$var1
	echo $var2
	if ( -e $var2) then
		echo $var2 'exists'
	else
		mkdir -p $var2
		echo 'Creating dir' $var2
	echo "Creating input file for" $var2
	ls $dir >  $var2"/batch_input.in"
end
