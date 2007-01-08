#!/usr/bin/perl

use warnings;
use strict;

for my $fileName (glob "./*.results") {
    open RESULTS, $fileName or die "can't open $fileName: $!";
    my $totalTime = 0;
    my $totalBandwidth = 0;
    my $totalRuns = 0;
    foreach (<RESULTS>) {
        ++$totalRuns;
        chomp;
        my ($time, $bw) = split /:/;
        $totalTime += $time;
        $totalBandwidth += $bw;
    }
    my $avgTime = $totalTime/$totalRuns;
    my $avgBandwidth = $totalBandwidth/$totalRuns;
    print "$fileName: $avgTime s, $avgBandwidth MB/sec\n"
}
