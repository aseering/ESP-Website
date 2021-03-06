from django import template
from django.shortcuts import render_to_response
from django.core.cache import cache
from esp.datatree.models import *
from esp.users.models import UserBit
from esp.web.util.template import cache_inclusion_tag, DISABLED
from esp.qsd.models import QuasiStaticData
from esp.qsd.models import qsd_cache_key
from urllib import quote

register = template.Library()

@cache_inclusion_tag(register,'inclusion/qsd/render_qsd.html', cache_time=300)
def render_qsd(qsd, user=None):
    edit_bits = False
    if user:
        edit_bits = UserBit.UserHasPerms(user, qsd.path, DataTree.get_by_uri('V/Administer/Edit'))
    return {'qsdrec': qsd, 'edit_bits': edit_bits}

@cache_inclusion_tag(register,'inclusion/qsd/render_qsd_inline.html', cache_time=1)
def render_inline_qsd(input_anchor, qsd, user=None):
    if isinstance(input_anchor, basestring):
        try:
            anchor = DataTree.get_by_uri(input_anchor)
        except DataTree.NoSuchNodeException:
            return {}
                
    elif isinstance(input_anchor, DataTree):
        anchor = input_anchor
    else:
        return {}

    edit_bits = False
    if user:
        edit_bits = UserBit.UserHasPerms(user, anchor, DataTree.get_by_uri('V/Administer/Edit'))
    qsd_obj = QuasiStaticData.objects.get_by_path__name(anchor, qsd)
    if qsd_obj == None:
        return {'edit_bits': edit_bits, 'qsdname': qsd, 'anchor_id': anchor.id}
    
    return {'qsdrec': qsd_obj, 'edit_bits': edit_bits}

    

class InlineQSDNode(template.Node):
    def __init__(self, nodelist, input_anchor, qsd_name, user_variable):
        self.nodelist = nodelist
        self.qsd_name = qsd_name
        self.user_variable = template.Variable(user_variable)
        self.input_anchor = input_anchor
        
    def render(self, context):
        try:
            user = self.user_variable.resolve(context)
        except template.VariableDoesNotExist:
            user = None

        try:
            anchor = template.Variable(self.input_anchor)
            anchor = anchor.resolve(context)
        except:
            anchor = GetNode(self.input_anchor)

        qsd = self.qsd_name

        edit_bits = UserBit.UserHasPerms(user, anchor, DataTree.get_by_uri('V/Administer/Edit'))

        qsd_obj = QuasiStaticData.objects.get_by_path__name(anchor, qsd)
        if qsd_obj == None:
            new_qsd = QuasiStaticData()
            new_qsd.path = anchor
            new_qsd.name = qsd
            new_qsd.title = qsd
            new_qsd.content = self.nodelist.render(context)
            new_qsd.author = user
            
            if user.id:
                new_qsd.save()

            qsd_obj = new_qsd

        return render_to_response("inclusion/qsd/render_qsd_inline.html", {'qsdrec': qsd_obj, 'edit_bits': edit_bits}, context_instance=context).content
        
@register.tag
def inline_qsd_block(parser, token):
    tokens = token.split_contents()
    if len(tokens) == 3:
        iqb, input_anchor, qsd_name = tokens
        user_variable = ""
    elif len(tokens) == 4:
        iqb, input_anchor, qsd_name, user_variable = tokens
    else:
        raise Exception("Wrong number of inputs for %s, either 2 or 3 expected" % (tokens))
    
    nodelist = parser.parse(("end_inline_qsd_block",))
    parser.delete_first_token()
    
    return InlineQSDNode(nodelist, input_anchor, qsd_name, user_variable)
    
