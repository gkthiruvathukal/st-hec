#!/usr/bin/perl

use warnings;
use strict;

open RESULTS, $ARGV[0] or die $!;

my %results;

while (<RESULTS>) {
    chomp;
    my ($io, $locktype, $numbytes, $locktime, $writetime, $unlocktime, $synctime, $closetime, $totaltime, $mbps) = split /:/;
    if (!defined $results{$io}) {
        $results{$io} = {};
    }
    if (!defined $results{$io}->{$locktype}) {
        $results{$io}->{$locktype} = [];
    }
    $results{$io}->{$locktype}->[0]++;
    $results{$io}->{$locktype}->[1] += $mbps;
    $results{$io}->{$locktype}->[2] += $locktime;
    $results{$io}->{$locktype}->[3] += $writetime;
    $results{$io}->{$locktype}->[4] += $unlocktime;
    $results{$io}->{$locktype}->[5] += $synctime;
    $results{$io}->{$locktype}->[6] += $closetime;
    $results{$io}->{$locktype}->[7] += $totaltime;
}

foreach my $iotype (sort keys %results) {
    print "$iotype: \n";
    foreach my $locktype (sort keys %{$results{$iotype}}) {
        my $avgrate = $results{$iotype}->{$locktype}->[1] / 
                      $results{$iotype}->{$locktype}->[0];
        my $avglocktime = $results{$iotype}->{$locktype}->[2] / 
                      $results{$iotype}->{$locktype}->[0];
        my $avgwritetime = $results{$iotype}->{$locktype}->[3] / 
                      $results{$iotype}->{$locktype}->[0];
        my $avgunlocktime = $results{$iotype}->{$locktype}->[4] / 
                      $results{$iotype}->{$locktype}->[0];
        my $avgsynctime = $results{$iotype}->{$locktype}->[5] / 
                      $results{$iotype}->{$locktype}->[0];
        my $avgclosetime = $results{$iotype}->{$locktype}->[6] / 
                      $results{$iotype}->{$locktype}->[0];
        my $avgtotaltime = $results{$iotype}->{$locktype}->[7] / 
                      $results{$iotype}->{$locktype}->[0];
        printf "type %d: lock=%4.5fs, write=%4.5fs, unlock=%4.5fs, sync=%4.5fs, close=%4.5fs, total=%4.5fs, %3.5f Mb/s\n",
            ($locktype, $avglocktime, $avgwritetime, $avgunlocktime, $avgsynctime, $avgclosetime, $avgtotaltime, $avgrate);
    }
    print "\n";
}
