#!/usr/bin/env python
# StatsGen - Password Statistical Analysis tool
#
# This tool is part of PACK (Password Analysis and Cracking Kit)
#
# VERSION 0.0.3
#
# Copyright (C) 2013 Peter Kacherginsky
# All rights reserved.
#
# Please see the attached LICENSE file for additional licensing information.

import operator, string
from decimal import *

VERSION = "0.0.3"

class StatsGen:
    def __init__(self):
        self.output_file = None

        # Filters
        self.minlength   = None
        self.maxlength   = None
        self.simplemasks = None
        self.charsets    = None
        self.quiet = False
        self.debug = True

        # Stats dictionaries
        self.stats_length = dict()
        self.stats_simplemasks = dict()
        self.stats_advancedmasks = dict()
        self.stats_charactersets = dict()

        # Ignore stats with less than 1% coverage
        self.hiderare = False

        self.filter_counter = 0
        self.total_counter = 0

        # Minimum password complexity counters
        self.mindigit   = None
        self.minupper   = None
        self.minlower   = None
        self.minspecial = None

        self.maxdigit   = None
        self.maxupper   = None
        self.maxlower   = None
        self.maxspecial = None

        self.uniqecrackedpws = set()
        self.charcountdict = dict()
    def analyze_password(self, password):

        # Password length
        pass_length = len(password)

        # Character-set and policy counters
        digit = 0
        lower = 0
        upper = 0
        special = 0

        simplemask = list()
        advancedmask_string = ""

        # Detect simple and advanced masks
        for letter in password:
 
            if letter in string.digits:
                digit += 1
                advancedmask_string += "?d"
                if not simplemask or not simplemask[-1] == 'digit': simplemask.append('digit')

            elif letter in string.lowercase:
                lower += 1
                advancedmask_string += "?l"
                if not simplemask or not simplemask[-1] == 'string': simplemask.append('string')


            elif letter in string.uppercase:
                upper += 1
                advancedmask_string += "?u"
                if not simplemask or not simplemask[-1] == 'string': simplemask.append('string')

            else:
                special += 1
                advancedmask_string += "?s"
                if not simplemask or not simplemask[-1] == 'special': simplemask.append('special')


        # String representation of masks
        simplemask_string = ''.join(simplemask) if len(simplemask) <= 3 else 'othermask'

        # Policy
        policy = (digit,lower,upper,special)

        # Determine character-set
        if   digit and not lower and not upper and not special: charset = 'numeric'
        elif not digit and lower and not upper and not special: charset = 'loweralpha'
        elif not digit and not lower and upper and not special: charset = 'upperalpha'
        elif not digit and not lower and not upper and special: charset = 'special'

        elif not digit and lower and upper and not special:     charset = 'mixedalpha'
        elif digit and lower and not upper and not special:     charset = 'loweralphanum'
        elif digit and not lower and upper and not special:     charset = 'upperalphanum'
        elif not digit and lower and not upper and special:     charset = 'loweralphaspecial'
        elif not digit and not lower and upper and special:     charset = 'upperalphaspecial'
        elif digit and not lower and not upper and special:     charset = 'specialnum'

        elif not digit and lower and upper and special:         charset = 'mixedalphaspecial'
        elif digit and not lower and upper and special:         charset = 'upperalphaspecialnum'
        elif digit and lower and not upper and special:         charset = 'loweralphaspecialnum'
        elif digit and lower and upper and not special:         charset = 'mixedalphanum'
        else:                                                   charset = 'all'

        return (pass_length, charset, simplemask_string, advancedmask_string, policy)

    def generate_stats(self, passwords):
        """ Generate password statistics. """
        # track uniqe cracked password for the character count statistic
        self.uniqecrackedpws = set(passwords)
        for pw in self.uniqecrackedpws:
            try:
                self.charcountdict[len(pw)] += 1
            except KeyError:
                self.charcountdict[len(pw)] = 1
        for password in passwords:
            password = password.rstrip()

            if len(password) == 0:continue

            self.total_counter += 1  

            (pass_length,characterset,simplemask,advancedmask, policy) = self.analyze_password(password)
            (digit,lower,upper,special) = policy

            if (self.charsets == None    or characterset in self.charsets) and \
               (self.simplemasks == None or simplemask in self.simplemasks) and \
               (self.maxlength == None   or pass_length <= self.maxlength) and \
               (self.minlength == None   or pass_length >= self.minlength):

                self.filter_counter += 1

                if self.mindigit == None or digit < self.mindigit: self.mindigit = digit
                if self.maxdigit == None or digit > self.maxdigit: self.maxdigit = digit

                if self.minupper == None or upper < self.minupper: self.minupper = upper
                if self.maxupper == None or upper > self.maxupper: self.maxupper = upper

                if self.minlower == None or lower < self.minlower: self.minlower = lower
                if self.maxlower == None or lower > self.maxlower: self.maxlower = lower

                if self.minspecial == None or special < self.minspecial: self.minspecial = special
                if self.maxspecial == None or special > self.maxspecial: self.maxspecial = special

                if pass_length in self.stats_length:
                    self.stats_length[pass_length] += 1
                else:
                    self.stats_length[pass_length] = 1

                if characterset in self.stats_charactersets:
                    self.stats_charactersets[characterset] += 1
                else:
                    self.stats_charactersets[characterset] = 1

                if simplemask in self.stats_simplemasks:
                    self.stats_simplemasks[simplemask] += 1
                else:
                    self.stats_simplemasks[simplemask] = 1

                if advancedmask in self.stats_advancedmasks:
                    self.stats_advancedmasks[advancedmask] += 1
                else:
                    self.stats_advancedmasks[advancedmask] = 1


    def print_stats(self, uniques):
        """ Print password statistics. """

        print "\nLength Stats of Unique Cracked Passwords:"
        print '\n                        Password Length | Percentage'
        print '                           ------------------------------'
        pwchars = int()
        for (length,count) in sorted(self.charcountdict.iteritems(), key=lambda d: d[1], reverse=True):
            if self.hiderare and not count*100/self.filter_counter > 0: continue
            pwchars += (length * count)
            print "%40d: %02s%% (%d)" % (length, round(Decimal(str(count*100.0/self.filter_counter)), 2), count)
        try:
            averagepwlength = round(Decimal(str(pwchars/float(uniques))), 2)
        except ZeroDivisionError:
            averagepwlength = 0
        print '\n          Average Unique Cracked Password Length: ' + str(averagepwlength) + ' characters\n'

        print "\nCharacter-set Stats:\n"
        for (char,count) in sorted(self.stats_charactersets.iteritems(), key=operator.itemgetter(1), reverse=True):
            if self.hiderare and not count*100/self.filter_counter > 0: continue
            print "%40s: %02s%% (%d)" % (char, round(Decimal(str(count*100.0/self.filter_counter)), 2), count)

        print "\nPassword complexity:\n"
        print "                               digit: min(%s) max(%s)" % (self.mindigit, self.maxdigit)
        print "                               lower: min(%s) max(%s)" % (self.minlower, self.maxlower)
        print "                               upper: min(%s) max(%s)" % (self.minupper, self.maxupper)
        print "                             special: min(%s) max(%s)" % (self.minspecial, self.maxspecial)

        print "\nCommon Masks:\n"
        for (simplemask,count) in sorted(self.stats_simplemasks.iteritems(), key=operator.itemgetter(1), reverse=True):
            if self.hiderare and not count*100/self.filter_counter > 0: continue
            print "%40s: %02s%% (%d)" % (simplemask, round(Decimal(str(count*100.0/self.filter_counter)), 2), count)

        print "\nAdvanced Masks:\n"
        for (advancedmask,count) in sorted(self.stats_advancedmasks.iteritems(), key=operator.itemgetter(1), reverse=True):
            if count*100/self.filter_counter > 0:
                print "%40s: %02s%% (%d)" % (advancedmask, round(Decimal(str(count*100.0/self.filter_counter)), 2), count)

            if self.output_file:
                self.output_file.write("%s,%d\n" % (advancedmask,count))


