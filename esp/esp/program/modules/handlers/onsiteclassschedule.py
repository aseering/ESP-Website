
__author__    = "MIT ESP"
__date__      = "$DATE$"
__rev__       = "$REV$"
__license__   = "GPL v.2"
__copyright__ = """
This file is part of the ESP Web Site
Copyright (c) 2007 MIT ESP

The ESP Web Site is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

Contact Us:
ESP Web Group
MIT Educational Studies Program,
84 Massachusetts Ave W20-467, Cambridge, MA 02139
Phone: 617-253-4882
Email: web@esp.mit.edu
"""
from django.http     import HttpResponseRedirect
from esp.users.views import search_for_user
from esp.program.modules.base import ProgramModuleObj, needs_teacher, needs_student, needs_admin, usercheck_usetl, needs_onsite
from esp.program.modules.handlers import ProgramPrintables
from esp.users.models import ESPUser, UserBit
from esp.datatree.models import GetNode
from datetime         import datetime
class OnsiteClassSchedule(ProgramModuleObj):


    @needs_student
    def printschedule(self, request, *args, **kwargs):
        verb  = GetNode('V/Publish/Print')
        qsc   = self.program.anchor.tree_create(['Schedule'])

        if UserBit.objects.filter(user = self.user,
                                  verb = verb,
                                  qsc = qsc,
                                  enddate__gte = datetime.now()).count() == 0:
            newbit = UserBit(user = self.user, verb = verb,
                             qsc = qsc, recursive = False)

            newbit.save()

        return HttpResponseRedirect('/learn/%s/studentreg' % self.program.getUrlBase())

    @needs_student
    def studentschedule(self, request, *args, **kwargs):
        request.GET = {'extra': str(285), 'op':'usersearch',
                       'userid': str(self.user.id) }

        module = [module for module in self.program.getModules('manage')
                  if type(module) == ProgramPrintables        ][0]

        module.user = self.user
        module.program = self.program
        return module.studentschedules(request, *args, **kwargs)

        
    @needs_onsite
    def schedule_students(self, request, tl, one, two, module, extra, prog):
        """ Display a teacher eg page """

        user, found = search_for_user(request, ESPUser.getAllOfType('Student', False))
        if not found:
            return user
        
        self.user.switch_to_user(request,
                                 user,
                                 self.getCoreURL(tl),
                                 'OnSite Registration!',
                                 True)

        return HttpResponseRedirect('/learn/%s/studentreg' % self.program.getUrlBase())
