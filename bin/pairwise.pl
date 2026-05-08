#!/usr/bin/perl
use lib '/home/luholm/DaliLite.v5/bin/';
use strict;
use mpidali;

# demo program
if($#ARGV<5) { die "USAGE: $0 list1file list2file DALIDATDIR_1 DALIDATIR_2 JOBID TITLE NPARA\n"; }
my($list1file,$list2file,$DALIDATDIR_1,$DALIDATDIR_2,$JOBID,$TITLE,$NPARA)=@ARGV;
if($NPARA<2) { $NPARA=2; } # backwards compatibility

# lock directory
&lock();

# pslit list1 to soap/wolf
my $soaplist1='soaplist1';
my $wolflist1='wolflist1';
my(@list)=&split_list1($list1file,$DALIDATDIR_1,$soaplist1,$wolflist1);

# soap if needed
if(-s $soaplist1 > 1) {
	system("cp $soaplist1 list1 ; cp $list2file list2");
	&wolf('SOAP',$NPARA,$DALIDATDIR_1,$DALIDATDIR_2,0);
}
if(-s $wolflist1 > 1) {
	system("cp $wolflist1 list1 ; cp $list2file list2");
	&wolf('WOLF',$NPARA,$DALIDATDIR_1,$DALIDATDIR_2,0);
	&parsi($NPARA,$DALIDATDIR_1,$DALIDATDIR_2,0);
	&swaplist12();
	&wolf('WOLF',$NPARA,$DALIDATDIR_2,$DALIDATDIR_1,1);
        &parsi($NPARA,$DALIDATDIR_2,$DALIDATDIR_1,1);
  	&swaplist12();
}
# output HTML
&FSSP_output($list2file,$DALIDATDIR_1,$DALIDATDIR_2,$JOBID,$TITLE,@list);

# unlock directory
&unlock();       
 
exit();

