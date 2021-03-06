# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

## app configuration made easy. Look inside private/appconfig.ini
from gluon.contrib.appconfig import AppConfig
## once in production, remove reload=True to gain full speed
myconf = AppConfig(reload=True)


if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL(myconf.take('db.uri'), pool_size=myconf.take('db.pool_size', cast=int), check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## choose a style for forms
response.formstyle = myconf.take('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.take('forms.separator')


## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
service = Service()
plugins = PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.take('smtp.server')
mail.settings.sender = myconf.take('smtp.sender')
mail.settings.login = myconf.take('smtp.login')

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

db.define_table('materia',
                Field('anio', widget=SQLFORM.widgets.radio.widget, requires=IS_IN_SET(['1', '2', '3', '4', '5']), label='Año'),
                Field('nombre', unique=True),
                Field('anual', label='Carga Horaria Anual'),
                Field('primer_cuatrimestre', label='Carga Horaria 1C'),
                Field('segundo_cuatrimestre', label='Carga Horaria 2C'),
                format='%(nombre)s'
               )

db.define_table('correlativa',
                Field('materia', db.materia, unique=True),
                Field('rpc','list:reference materia', label='Regulares para Cursar', widget=SQLFORM.widgets.checkboxes.widget),
                Field('apc','list:reference materia', label='Aprobadas para Cursar', widget=SQLFORM.widgets.checkboxes.widget)
               )


db.define_table('estado_academico',
                Field('usuario',db.auth_user, default=auth.user_id, readable=True, writable=False, unique=True),
                Field('regulares','list:reference materia', label='Regulares', widget=SQLFORM.widgets.checkboxes.widget),
                Field('aprobadas','list:reference materia', label='Aprobadas', widget=SQLFORM.widgets.checkboxes.widget)
               )


db.define_table('turno',
                Field('descripcion', requires=IS_IN_SET(['Mañana','Tarde','Noche'])),
                Field('numero_turno', requires=IS_IN_SET(['0','1','2'])),
                format='%(numero_turno)s'
               )

db.define_table('modulo',
                Field('turno', db.turno),
                Field('hora_inicio', type='time' ,label="Hora de Inicio"),
                Field('numero_modulo', requires=IS_IN_SET(['-1','0','1','2','3','4','5','6','7'])),
                format='%(numero_modulo)s'
               )


db.define_table('horario_clases',
                Field('turno', db.turno),
                Field('materia', db.materia, label='Materia'),
                Field('comision', requires=IS_IN_SET(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']), label='Comisión'),
                Field('dia', requires=IS_IN_SET(['1', '2', '3', '4', '5']), label='Día'),
                Field('modulo','list:reference modulo', label='Módulo', widget=SQLFORM.widgets.checkboxes.widget)
               )

for table in db.tables():
    db[table].id.readable = False



## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

mail.settings.server = settings.email_server
mail.settings.sender = settings.email_sender
mail.settings.login = settings.email_login
