#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2024-2025  Stephen Cuka                                       #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %color = ();
my %cgiparams = ();
my %mainsettings = ();
my %speedtest_settings = ();
my %checked = ();
my %selected = ();
my @dayhours = (0..23);
my @run_timesperday = ('1', '2', '3', '4', '6', '8', '12', '24');
my ($day, $month, $year) = (localtime(time))[3,4,5];
my $today = sprintf '%04d-%02d-%02d', $year+1900, $month+1, $day;
($day, $month, $year) = (localtime(time + 86400))[3,4,5];
my $tomorrow = sprintf '%04d-%02d-%02d', $year+1900, $month+1, $day;
my $datapertest = 420;
my $speedtestinstalled = "";
my $speedtestrunning = "";
my @speedtestresults = "";
my $displaytext = "";
my @statsout = "";
my @logrecords = "";

my $settings_file = "${General::swroot}/speedtest-webgui/settings";
unless (-f $settings_file) { &General::system("mkdir", "${General::swroot}/speedtest-webgui") };
unless (-f $settings_file) { &General::system("touch", "$settings_file") };

# default settings
$cgiparams{'LOGSPEEDTEST'} = 'off';
$cgiparams{'LOGFILE'} = '';
$cgiparams{'TESTTYPE'} = 'both';
$cgiparams{'FILEFORMAT'} = 'json';
$cgiparams{'STARTHOUR'} = '0';
$cgiparams{'TIMESPERDAY'} = '1';
$cgiparams{'USEDATES'} = 'off';
$cgiparams{'STARTDATE'} = '';
$cgiparams{'ENDDATE'} = '';
$cgiparams{'SERVER'} = 'auto';
$cgiparams{'ACTION'} = '';
&Header::getcgihash(\%cgiparams);

&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/ipfire/include/colors.txt", \%color);

if ( -e "/usr/bin/speedtest-cli" )
{
    $speedtestinstalled = "true";
}

if ( ($cgiparams{'ACTION'} eq "@{[ _('Run Speedtest') ]}") ||
          ($cgiparams{'ACTION'} eq "@{[ _('Start') ]}") ||
          ($cgiparams{'ACTION'} eq "@{[ _('Clear') ]}") )
{

    $speedtestrunning = `ps -ef | grep /usr/bin/speedtest | grep -v grep`;

    &Header::showhttpheaders();
    &Header::openpage(_('Speedtest'), 1, '');
    &Header::openbigbox('100%', 'left', '', '');
    &Header::openbox('100%', 'left', _('Run Speedtest and Display to Screen'));

    print <<END
    <form method='post' action='$ENV{'SCRIPT_NAME'}' onkeydown='if(event.keyCode ===13) {return false;}'>
    <table width='100%'>
    <tr>
        <td align='center'>
        <button disabled id='startbutton' type='submit' name='ACTION' value='@{[_('Start')]}' style='margin-bottom:16px'>@{[_('Start')]}</button>&nbsp
        <button disabled id='clearbutton' type='submit' name='ACTION' value='@{[_('Clear')]}' style='margin-bottom:16px'>@{[_('Clear')]}</button>
        </td>
    </tr>
    <tr>
      <td>
      <textarea id='displayarea' style='width:100%;resize:none' rows='15' cols='80' readonly='readonly'>
    placeholder text
      </textarea>
      </td>
    </tr'>
    <tr>
        <td align='center'>
        <input disabled type='submit' id='backbutton' name='ACTION' value='@{[_('Back')]}' style='margin-top:14px;margin-bottom:4px'>
        </td>
    </tr>
    </table>
    </form>
END
;

    &Header::closebox();

    if (! $speedtestinstalled)
    {
        $displaytext = _('The speedtest-cli addon is not installed.') . "\\n\\n" . _('Install speedtest-cli with Pakfire.');
        print <<END
        <script>
            document.getElementById('displayarea').value = '$displaytext';
            document.getElementById('backbutton').disabled = false;
        </script>
END
;
    } else {
        if ($speedtestrunning)
        {
            $displaytext = _('Speedtest is already running.  Try again later...');
            print <<END
            <script>
                document.getElementById('displayarea').value = '$displaytext';
                document.getElementById('clearbutton').disabled = false;
                document.getElementById('backbutton').disabled = false;
            </script>
END
;
        } else {
            if ( $cgiparams{'ACTION'} eq "@{[ _('Start') ]}" )
            {
                $displaytext = _('Running Speedtest, please wait...') . "\\n";
                print <<END
                <script>
                    document.getElementById('displayarea').value = '$displaytext';
                </script>
END
;
                @speedtestresults = `speedtest-cli --secure 2>&1`;
                chomp @speedtestresults;
                foreach (@speedtestresults)
                {
                    $displaytext = $displaytext . "\\n" . $_;
                }
                $displaytext = $displaytext . "\\n\\n" . _('Test complete.');
                print <<END
                <script>
                    document.getElementById('displayarea').value = '$displaytext';
                    document.getElementById('clearbutton').disabled = false;
                    document.getElementById('backbutton').disabled = false;
                </script>
END
;
            } else {
                $displaytext = _('Press Start to run Speedtest...');
                print <<END
                <script>
                    document.getElementById('displayarea').value = '$displaytext';
                    document.getElementById('startbutton').disabled = false;
                    document.getElementById('clearbutton').disabled = false;
                    document.getElementById('backbutton').disabled = false;
                </script>
END
;
            }
        }
    }

    &Header::closebigbox();
    &Header::closepage();

} else {
    if ($cgiparams{'ACTION'} eq "@{[ _('Save') ]}")
    {
        $speedtest_settings{'LOGSPEEDTEST'} = $cgiparams{'LOGSPEEDTEST'};
        $speedtest_settings{'LOGFILENAME'} = $cgiparams{'LOGFILENAME'};
        $speedtest_settings{'TESTTYPE'} = $cgiparams{'TESTTYPE'};
        $speedtest_settings{'FILEFORMAT'} = $cgiparams{'FILEFORMAT'};
        $speedtest_settings{'STARTHOUR'} = $cgiparams{'STARTHOUR'};
        $speedtest_settings{'TIMESPERDAY'} = $cgiparams{'TIMESPERDAY'};
        $speedtest_settings{'USEDATES'} = $cgiparams{'USEDATES'};
        $speedtest_settings{'STARTDATE'} = $cgiparams{'STARTDATE'};
        $speedtest_settings{'ENDDATE'} = $cgiparams{'ENDDATE'};
        $speedtest_settings{'SERVER'} = $cgiparams{'SERVER'};
        if ($speedtest_settings{'LOGSPEEDTEST'} eq "off")
        {
            $speedtest_settings{'LOGFILENAME'} = "";
            $speedtest_settings{'TESTTYPE'} = "";
            $speedtest_settings{'FILEFORMAT'} = "";
            $speedtest_settings{'STARTHOUR'} = "";
            $speedtest_settings{'TIMESPERDAY'} = "";
            $speedtest_settings{'USEDATES'} = "";
            $speedtest_settings{'STARTDATE'} = "";
            $speedtest_settings{'ENDDATE'} = "";
            $speedtest_settings{'SERVER'} = "";
        }
        &General::writehash("$settings_file", \%speedtest_settings);
    }

    &General::readhash("$settings_file", \%speedtest_settings);

    if ($speedtest_settings{'LOGSPEEDTEST'})
    {
        $cgiparams{'LOGSPEEDTEST'} = $speedtest_settings{'LOGSPEEDTEST'};
    } else {
        $cgiparams{'LOGSPEEDTEST'} = 'off';
    }

    if ($speedtest_settings{'LOGFILENAME'})
    {
        $cgiparams{'LOGFILENAME'} = $speedtest_settings{'LOGFILENAME'};
    } else {
        if ($cgiparams{'FILEFORMAT'} eq "csv")
        {
            $cgiparams{'LOGFILENAME'} = '/var/log/speedtest.csv.log';
        } else {
            $cgiparams{'LOGFILENAME'} = '/var/log/speedtest.json.log';
        }
    }

    if ($speedtest_settings{'TESTTYPE'})
    {
        $cgiparams{'TESTTYPE'} = $speedtest_settings{'TESTTYPE'};
    } else {
        $cgiparams{'TESTTYPE'} = 'both';
    }

    if ($speedtest_settings{'FILEFORMAT'})
    {
        $cgiparams{'FILEFORMAT'} = $speedtest_settings{'FILEFORMAT'};
    } else {
        $cgiparams{'FILEFORMAT'} = 'json';
    }

    if ($speedtest_settings{'STARTHOUR'})
    {
        $cgiparams{'STARTHOUR'} = $speedtest_settings{'STARTHOUR'};
    } else {
        $cgiparams{'STARTHOUR'} = '0';
    }

    if ($speedtest_settings{'TIMESPERDAY'})
    {
        $cgiparams{'TIMESPERDAY'} = $speedtest_settings{'TIMESPERDAY'};
    } else {
        $cgiparams{'TIMESPERDAY'} = '1';
    }

    if ($speedtest_settings{'USEDATES'})
    {
        $cgiparams{'USEDATES'} = $speedtest_settings{'USEDATES'};
    } else {
        $cgiparams{'USEDATES'} = 'off';
    }

    if ($speedtest_settings{'STARTDATE'})
    {
        $cgiparams{'STARTDATE'} = $speedtest_settings{'STARTDATE'};
    } else {
        $cgiparams{'STARTDATE'} = '';
    }

    if ($speedtest_settings{'ENDDATE'})
    {
        $cgiparams{'ENDDATE'} = $speedtest_settings{'ENDDATE'};
    } else {
        $cgiparams{'ENDDATE'} = '';
    }

    if ($speedtest_settings{'SERVER'})
    {
        $cgiparams{'SERVER'} = $speedtest_settings{'SERVER'};
    } else {
        $cgiparams{'SERVER'} = 'auto';
    }

    $checked{'LOGSPEEDTEST'}{'off'} = '';
    $checked{'LOGSPEEDTEST'}{'on'} = '';
    $checked{'LOGSPEEDTEST'}{$cgiparams{'LOGSPEEDTEST'}} = "checked='checked'";

    $selected{'TESTTYPE'}{'both'} = '';
    $selected{'TESTTYPE'}{'download'} = '';

    $selected{'TESTTYPE'}{$cgiparams{'TESTTYPE'}} = "selected='selected'";

    $selected{'FILEFORMAT'}{'csv'} = '';
    $selected{'FILEFORMAT'}{'json'} = '';
    $selected{'FILEFORMAT'}{$cgiparams{'FILEFORMAT'}} = "selected='selected'";

    map ($selected{'STARTHOUR'}{$_} = '', @dayhours);
    $selected{'STARTHOUR'}{$cgiparams{'STARTHOUR'}} = "selected='selected'";

    map ($selected{'TIMESPERDAY'}{$_} = '', @run_timesperday);
    $selected{'TIMESPERDAY'}{$cgiparams{'TIMESPERDAY'}} = "selected='selected'";

    $checked{'USEDATES'}{'off'} = '';
    $checked{'USEDATES'}{'on'} = '';
    $checked{'USEDATES'}{$cgiparams{'USEDATES'}} = "checked='checked'";

    &Header::showhttpheaders();
    &Header::openpage(_('Speedtest'), 1, '');
    &Header::openbigbox('100%', 'left');
    &Header::openbox('100%','left',_('Run Speedtest and Display to Screen'));

    print <<END
    <form method='post' action='$ENV{'SCRIPT_NAME'}' onkeydown='if(event.keyCode ===13) {return false;}'>
    <table width='100%'>
    <tr>
        <td align='center'>
END
;

    if ($speedtestinstalled)
    {
        print "<input type='submit' id='runbutton' name='ACTION' value='@{[ _('Run Speedtest') ]}' style='margin-bottom:4px'>";
    } else {
        print "<a href='/cgi-bin/pakfire.cgi'><strong>@{[ _('Install speedtest-cli With Pakfire') ]}</strong></a>";
    }

    print <<END
        </td>
    </tr>
    </table>
    </form>
END
;

    &Header::closebox();
    &Header::openbox('100%','left',_('Schedule Speedtest to Run and Log to File'));

    print <<END
    <script>
    function validateForm() {
        let sdate = document.getElementById('startdate').value;
        let edate = document.getElementById('enddate').value;
        if (usedates.checked == false)
            {
                // write all elements even if they were disabled
                document.getElementById('testtype').disabled = false;
                document.getElementById('fileformat').disabled = false;
                document.getElementById('timesperday').disabled = false;
                document.getElementById('usedates').disabled = false;
                document.getElementById('startdate').disabled = false;
                document.getElementById('enddate').disabled = false;
            } else if ( sdate == '' || edate == '' )
                {
                    document.getElementById('startdate').style.color = 'red';
                    document.getElementById('enddate').style.color = 'red';
                    document.getElementById('datemsg').innerHTML = "@{[_('Enter both a Start and End Date')]}";
                    document.getElementById('datemsg').style.visibility = 'visible';
                    return false;
                } else if ( sdate >= edate )
                    {
                        document.getElementById('startdate').style.color = 'red';
                        document.getElementById('enddate').style.color = 'red';
                        document.getElementById('datemsg').innerHTML = "@{[_('End Date must be after Start Date')]}";
                        document.getElementById('datemsg').style.visibility = 'visible';
                        return false;
                   }
        return true;
    }

    function enableLogSpeedtest() {
        let date = new Date();
        let y = date.getFullYear();
        let m = ('0' + (date.getMonth() + 1)).slice(-2);
        let d = ('0' + date.getDate()).slice(-2);
        let today = y + '-' + m + '-' + d;
        let edate = document.getElementById('enddate').value;
        if ( logspeedtest.checked )
        {
            document.getElementById('testtype').disabled = false;
            document.getElementById('fileformat').disabled = false;
            document.getElementById('starthour').disabled = false;
            checkStartHour();
            document.getElementById('hourmsg').style.visibility = 'visible';
            document.getElementById('timesperday').disabled = false;
            updateDataEstimate();
            document.getElementById('datamsg').style.visibility = 'visible';
            document.getElementById('usedates').disabled = false;
            if ( usedates.checked )
            {
                document.getElementById('startdate').disabled = false;
                document.getElementById('enddate').disabled = false;
                if ( edate < today )
                {
                    document.getElementById('datemsg').innerHTML = "@{[_('Date window has expired.  Speedtest will not run.')]}";
                    document.getElementById('datemsg').style.visibility = 'visible';
                }
            }
            document.getElementById('servername').disabled = false;
        } else {
            // set defaults
            document.getElementById('testtype').value = 'both';
            document.getElementById('fileformat').value = 'json';
            document.getElementById('logfilename').innerHTML = '/var/log/speedtest.json.log';
            document.getElementById('logfilenameinput').value = '/var/log/speedtest.json.log';
            document.getElementById('starthour').value = 0;
            document.getElementById('timesperday').value = 1;
            document.getElementById('usedates').checked = false;
            document.getElementById('startdate').value = '';
            document.getElementById('enddate').value = '';
            document.getElementById('servername').value = 'auto';
            document.getElementById('testtype').disabled = true;
            document.getElementById('fileformat').disabled = true;
            document.getElementById('starthour').disabled = true;
            document.getElementById('hourmsg').innerHTML = '';
            document.getElementById('hourmsg').style.visibility = 'hidden';
            document.getElementById('timesperday').disabled = true;
            document.getElementById('datamsg').innerHTML = '';
            document.getElementById('datamsg').style.visibility = 'hidden';
            document.getElementById('usedates').disabled = true;
            document.getElementById('startdate').style.color = 'black';
            document.getElementById('startdate').value = '';
            document.getElementById('startdate').disabled = true;
            document.getElementById('enddate').style.color = 'black';
            document.getElementById('enddate').value = '';
            document.getElementById('enddate').disabled = true;
            document.getElementById('datemsg').innerHTML = "@{[_('End Date must be after Start Date')]}";
            document.getElementById('datemsg').style.visibility = 'hidden';
            document.getElementById('servername').disabled = true;
        }
    }

    function updateLogfilename() {
        let a = document.getElementById('fileformat').value;
        if ( a == 'csv' )
        {
            document.getElementById('logfilename').innerHTML = '/var/log/speedtest.csv.log';
            document.getElementById('logfilenameinput').value = '/var/log/speedtest.csv.log';
        } else {
            document.getElementById('logfilename').innerHTML = '/var/log/speedtest.json.log';
            document.getElementById('logfilenameinput').value = '/var/log/speedtest.json.log';
        }
    }

    function toggleDateEntry() {
        if ( usedates.checked )
        {
            document.getElementById('startdate').disabled = false;
            document.getElementById('enddate').disabled = false;
        } else {
            document.getElementById('startdate').disabled = true;
            document.getElementById('enddate').disabled = true;
            document.getElementById('startdate').value = '';
            document.getElementById('enddate').value = '';
            document.getElementById('startdate').style.color = 'black';
            document.getElementById('enddate').style.color = 'black';
            document.getElementById('datemsg').style.visibility = 'hidden';
            checkStartHour();
        }
    }

    function checkDates() {
        let sdate = document.getElementById('startdate').value;
        let edate = document.getElementById('enddate').value;
        if ( sdate == '' || edate == '' )
        {
            // date entry not complete
            document.getElementById('startdate').style.color = 'black';
            document.getElementById('enddate').style.color = 'black';
            document.getElementById('datemsg').style.visibility = 'hidden';
        } else if ( sdate != '' && edate != '' && edate > sdate )
            {
                // ok:  enddate > startdate
                document.getElementById('startdate').style.color = 'black';
                document.getElementById('enddate').style.color = 'black';
                document.getElementById('datemsg').style.visibility = 'hidden';
                checkStartHour();
            } else {
                // error:  enddate < startdate
                document.getElementById('startdate').style.color = 'red';
                document.getElementById('enddate').style.color = 'red';
                document.getElementById('datemsg').style.color = 'red';
                document.getElementById('datemsg').innerHTML = "@{[_('End Date must be after Start Date')]}";
                document.getElementById('datemsg').style.visibility = 'visible';
            }
        return;
    }

    function getFirstRuntime(interval, shour) {
        let lowhour = 24;
        for ( let i = 1; i <= 24; i++ )
        {
            let r = i % interval;
            if ( r == 0 )
            {
                let j = i - interval + Number(shour);
                if (j < 0)
                {
                    j = j + 24;
                }
                if (j > 23)
                {
                    j = j - 24;
                }
                if ( j < lowhour )
                {
                    lowhour = j;
                }
            }
        }
        return lowhour;
    }

    function getNextRuntime(hour, interval, shour) {
        let lowhour = 24;
        for ( let i = 1; i <= 24; i++ )
        {
            let r = i % interval;
            if ( r == 0 )
            {
                let j = i - interval + Number(shour);
                if (j < 0)
                {
                    j = j + 24;
                }
                if (j > 23)
                {
                    j = j - 24;
                }
                if ( j > hour )
                {
                    if ( j < lowhour )
                    {
                        lowhour = j;
                    }
                }
            }
        } 
        if ( lowhour < 24 )
        {
            return lowhour;
        } else {
            return -1;
        }
    }

    function convertHourToAmPm(hour) {
        if ( hour < 12 )
        {
            return hour + ':00 AM';
        } else {
            if ( hour == 12 )
            {
                return hour + ':00 PM';
            } else {
                return (hour - 12) + ':00 PM';
            }
        }
    }

    function setHourmsg(runtime, date) {
        if ( date == undefined )
        {
            msgtext = "    @{[_('Next run time:')]}" + '  ' + convertHourToAmPm(runtime);
            document.getElementById('hourmsg').style.color = 'black';
            document.getElementById('hourmsg').style.visibility = 'visible';
            document.getElementById('hourmsg').innerHTML = msgtext;
        } else {
            let year = date.substr(0, 4);
            let monthday = date.substr(5);
            let displaydate = monthday + '-' + year;
            msgtext = "    @{[_('Next run time:')]}" + '  ' + convertHourToAmPm(runtime) + ' @{['on']} ' + displaydate;
            document.getElementById('hourmsg').style.color = 'black';
            document.getElementById('hourmsg').style.visibility = 'visible';
            document.getElementById('hourmsg').innerHTML = msgtext;
        }
        return
    }

    function checkStartHour() {
        let date = new Date();
        let hour = date.getHours();
        let y = date.getFullYear();
        let m = ('0' + (date.getMonth() + 1)).slice(-2);
        let d = ('0' + date.getDate()).slice(-2);
        let today = y + '-' + m + '-' + d;
        date.setDate(date.getDate() + 1);
        d = ('0' + date.getDate()).slice(-2);
        let tomorrow = y + '-' + m + '-' + d;
        let shour = document.getElementById('starthour').value;
        let tpd = document.getElementById('timesperday').value;
        let sdate = document.getElementById('startdate').value;
        let interval = 24 / tpd;
        let nextrun = getNextRuntime(hour, interval, shour);
        let firstrun = getFirstRuntime(interval, shour);
        if ( sdate == '' )
        {
            if ( nextrun == -1 )
            {
                setHourmsg(nextrun, tomorrow);
            } else {
                setHourmsg(nextrun);
            }
        }
        if ( sdate > today )
        {
            setHourmsg(firstrun, sdate);
        }
        if ( sdate <= today )
        {
            if ( nextrun == -1 )
            {
                setHourmsg(firstrun, tomorrow);
            } else {
                setHourmsg(nextrun);
            }
        }
        return;
    }

    function updateDataEstimate() {
        let a = document.getElementById('timesperday').value;
        let b = a * $datapertest;
        let datamessage = "    @{[_('Estimated daily data use at')]} " + $datapertest + 'MB' + "@{[_(' per test:  ')]}" + b + 'MB';
        document.getElementById('datamsg').innerHTML = datamessage;
    }
    </script>

    <form method='post' action='$ENV{'SCRIPT_NAME'}' onkeydown='if(event.keyCode ===13) {return false;}' onsubmit='return validateForm()'>
    <table width='100%'>

    <caption style='text-align:left;font-size:110%'>@{[_('When enabled, speedtest will run at intervals and the results will be written to the /var/log directory.')]}</caption>

    <colgroup>
        <col width='3%'>
        <col width='10%'>
        <col width='87%'>
    </colgroup

    <tr>
        <td style='height:32px'>
        <input type='checkbox' id='logspeedtest' name='LOGSPEEDTEST' $checked{'LOGSPEEDTEST'}{'on'} onclick='enableLogSpeedtest()'/>
        <td>@{[_('Enabled')]}</td>
        </td>
    </tr>

    <tr>
        <td></td>
        <td colspan='2'>@{[_('Select the test type:')]}</td>
    </tr>
    <tr>
        <td></td>
        <td colspan='2'>
        <select id='testtype' name='TESTTYPE' disabled style='margin-bottom:16px'>
        <option value='both' $selected{'TESTTYPE'}{'both'}>@{[_('Download and Upload')]}</option>
        <option value='download' $selected{'TESTTYPE'}{'download'}>@{[_('Download Only')]}</option>
        <option value='upload' $selected{'TESTTYPE'}{'upload'}>@{[_('Upload Only')]}</option>
        </select>
    </td>
    </tr>

    <tr>
        <td></td>
        <td colspan='2'>@{[_('Select the output format:')]}</td>
    </tr>
    <tr>
        <td></td>
        <td colspan='2'>
        <select id='fileformat' name='FILEFORMAT' onchange='updateLogfilename()' disabled style='margin-bottom:16px'>
        <option value='csv' $selected{'FILEFORMAT'}{'csv'}>CSV</option>
        <option value='json' $selected{'FILEFORMAT'}{'json'}>JSON</option>
        </select>    @{[_('Speedtest results will be written to:')]}  
        <text id='logfilename' style='font-weight:bold'>$cgiparams{'LOGFILENAME'}</text>
        <input id='logfilenameinput' name='LOGFILENAME' style='display:none' value='$cgiparams{'LOGFILENAME'}'/>
    </tr>

    <tr>
        <td></td>
        <td colspan='2'>@{[_('Select the number of times per day to run speedtest:')]}</td>
    </tr>
    <tr>
        <td></td>
        <td colspan='2'>
        <select id='timesperday' name='TIMESPERDAY' onchange='updateDataEstimate(); checkStartHour()' disabled style='margin-bottom:16px'>
END
;

    foreach (@run_timesperday)
    {
        if ($_ == 1)
        {
            print "\t<option value='$_' $selected{'TIMESPERDAY'}{$_}>@{[ _('Run Speedtest') ]} $_ @{[ _('time per day') ]}</option>\n";
        } else {
            print "\t<option value='$_' $selected{'TIMESPERDAY'}{$_}>@{[ _('Run Speedtest') ]} $_ @{[ _('times per day') ]}</option>\n";
        }
    }

    print <<END
        </select><text id='datamsg' style='visibility:hidden'>datamsg placeholder</text>
        <td>
    </tr>

    <tr>
        <td></td>
        <td colspan='2'>@{[_('Select the start hour to use when calculating run times:')]}</td>
    </tr>
    <tr>
        <td></td>
        <td colspan='2'><select id='starthour' name='STARTHOUR' onchange='checkStartHour()' disabled style='margin-bottom:16px'>
END
;

    my $ampm = '';
    my $displayhour = 0;
    for (@dayhours)
    {
        if ($_ <= 11)
        {
            if ($_ == 0)
            {
                $ampm = 'AM ' . _('- Midnight');
            } else {
                $ampm = 'AM';
            }
	    $displayhour = $_;
        } else {
            if ($_ == 12)
            {
                $ampm = 'PM ' . _('- Noon');
                $displayhour = $_;
            } else {
                $ampm = 'PM';
                $displayhour = $_ - 12;
            }
        }
        print "\t<option value='$_' $selected{'STARTHOUR'}{$_}>$displayhour:00 $ampm</option>\n";
    }

    print <<END
        </select><text id='hourmsg' style='visibility:hidden'>hourmsg placeholder</text>
        <td>
    </tr>
END
;

    print <<END    
    <tr>
        <td></td>
        <td colspan='2' style='height:32px'>
        <input type='checkbox' id='usedates' name='USEDATES' onclick='toggleDateEntry()' $checked{'USEDATES'}{'on'} disabled/>    @{[_('Use Start and End Dates:')]}</td>
    </tr>
    <tr>
        <td></td>
        <td>@{[_('Start Date:')]}</td>
        <td>
        <input type=date id='startdate' name='STARTDATE' value='$cgiparams{'STARTDATE'}' min='$today' disabled oninput='checkDates()'>
        </td>
    </tr>
    <tr>
        <td></td>
        <td>@{[_('End Date:')]}</td>
        <td>
        <input type=date id='enddate' name='ENDDATE' value='$cgiparams{'ENDDATE'}' min='$tomorrow' disabled oninput='checkDates()'>
        </td>
    </tr>
    <tr>
        <td></td>
        <td colspan='2' id='datemsg' style='color:red;visibility:hidden'>@{[_('End Date must be after Start Date')]}</td>
    </tr>

    <tr>
        <td></td>
        <td colspan='2'>@{[_('Have speedtest automatically select a server or select one from the list:')]}</td>
    </tr>
    <tr>
        <td></td>
        <td colspan='2'>
        <select id='servername' name='SERVER' disabled>
        <option value='auto''>@{[_('Automatically Select Server')]}</option>
END
;

    if ($speedtestinstalled)
    {
        # build server options for speedtest-cli
        my @serverlist = ();
        @serverlist = `speedtest-cli --secure --list`;
        splice(@serverlist, 0, 1);
        for (@serverlist)
        {
            print "<option value='$_' ";
            chomp ( $_, $cgiparams{'SERVER'} );
            $_ =~ s/^\s+//;
            $cgiparams{'SERVER'} =~ s/^\s+//;
            if ( "$_" eq "$cgiparams{'SERVER'}" )
            {
                print "selected='selected'";
            }
                print ">$_</option>\n";
        }
    }

    print <<END
        </select>
        </td>
    </tr>

    <tr>
        <td colspan='3' align='center'>
        <input type='submit' id='savebutton' name='ACTION' value='@{[_('Save')]}' style='margin-top:16px;margin-bottom:4px'>
        </td>
    </tr>
    </table>
    </form>
END
;

    &Header::closebox();

    if ($speedtestinstalled eq "true")
    {
        print <<END
        <script>
            document.getElementById('logspeedtest').disabled = false;
            enableLogSpeedtest();
        </script>
END
;
    } else {
        print <<END
        <script>
            document.getElementById('logspeedtest').disabled = true;
            document.getElementById('savebutton').disabled = true;
        </script>
END
;
    }

    #&Header::openbox('100%','left',_('Status'));
    &Header::openbox('100%','left','Status');

    if ($cgiparams{'LOGSPEEDTEST'} eq "off")
    {
    print "<textarea style='width:100%;resize:none' rows='2' cols='80' readonly='readonly'>";
        print "@{[ _('Schedule Speedtest to Run and Log to File is Not Enabled.') ]}";
    } else {
    print "<textarea style='width:100%;resize:none' rows='13' cols='80' readonly='readonly'>";
        if ( -e $cgiparams{'LOGFILENAME'} )
        {
            @statsout = `stat --format='%y' $settings_file`;
            $statsout[0] = substr($statsout[0], 0, 19);
            print "@{[ _('Settings last saved on:') ]}  ";
            print "@statsout";
            print "\n\n@{[ _('Logging to file:') ]}  $cgiparams{'LOGFILENAME'}\n\n";
            @statsout = `stat --format='%s' $cgiparams{'LOGFILENAME'}`;
            print "@{[ _('Logfile size:') ]}  ";
            print "@statsout";
            print "\n@{[ _('Number of records in logfile:') ]}  ";
            @statsout = `wc -l $cgiparams{'LOGFILENAME'} | cut -d/ -f1`;
            print "@statsout";
            @statsout=`ls $cgiparams{'LOGFILENAME'}*`;
            $statsout[0] = " " . $statsout[0];
            print "\n@{[ _('All speedtest logfiles:') ]}\n\n";
            print "@statsout";
        } else {
            print "@{[ _('Logfile not found.  It will be created the next time speedtest runs.') ]}";
        }
    }
    print "</textarea>";

    &Header::closebox();

    &Header::openbox('100%','left', _('Last 10 Log Records'));

    if ($cgiparams{'LOGSPEEDTEST'} eq "off")
    {
    print "<textarea id='recordarea' style='width:100%;resize:vertical' rows='2' cols='80' readonly='readonly'>";
        print "@{[ _('Schedule Speedtest to Run and Log to File is Not Enabled.') ]}";
    } else {
    print "<textarea id='recordarea' style='width:100%;resize:vertical' rows='13' cols='80' readonly='readonly'>";
        if ( -e $cgiparams{'LOGFILENAME'} )
        {
            @logrecords = `tail -n 10 $cgiparams{'LOGFILENAME'}`;
            chomp @logrecords;
            foreach (@logrecords)
            {
                print $_ . "\n\n";
            }
        } else {
            print "@{[ _('Logfile not found.  It will be created the next time speedtest runs.') ]}";
        }
    }
    print "</textarea>";
    print "<script> recordarea.scrollTop = 1000; </script>";

    &Header::closebox();
    &Header::closebigbox();
    &Header::closepage();
}
