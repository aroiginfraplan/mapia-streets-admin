# Mapia Streets Admin

Projecte de Django 3.2 administrador de MapiaStreets

## Context Info APIs

Les APIs d'informació de context de Mapia Streets depenen de cada client/instància. Algunes APIs poden estar disponibles per tots els clients mentre que d'altres poden estar disponibles només per determinats clients.

### Django Admin

Al django admin, a la pàgina d'edició d'una campanya, hi ha un camp Context Info APIs on podem triar la informació de context que volem mostrar segons la campanya a l'iframe del panorama dins el frontend de Mapia Streets.

En aquest desplegable hi apareixen només les opcions disponibles en aquell servidor (és a dir, per aquell client).

### Codi

A la carpeta `tenants` hi ha una carpeta `core` i una carpeta per cada client. A `core` hi ha recursos comuns per tots els clients, mentre que a les carpetes de client hi ha els recursos que només s'executaran en cas que el servidor on estigui instal·lada la app sigui el d'aquell client.

#### Definició del client
Per indicar a quin client pertany aquella instància definirem la variable d'entorn `APP_CLIENT_NAME`, posant-li el mateix nom que li posarem a la carpeta.

#### Definició de les APIs disponibles
Les APIs que apareixeran com a opcions al desplegable han d'estar definides als fitxers `context_info.py`.

- A `tenants/core/context_info.py` hi posarem les APIs que hagin d'estar disponibles per tots els clients per defecte o que hagin d'estar accessibles per més d'un client.
- A `tenants/<APP_SITE_NAME>/context_info.py` hi posarem les APIs que només estiguin disponibles per un únic client.

Si volem crear una nova API d'informació de context, la crearem al lloc on toqui i sempre com una classe que exten la classe `ContextInfoAPI` definida a `core`.

En aquesta nova subclasse hem de definir els mètodes `get_url` i `get_values` (en trobareu més informació a la pròpia classe base `ContextInfoAPI`).

#### Assignar APIs a clients
- **Core**: en cas que haguem creat la classe a `core` i vulguem:
    - que la API estigui sempre disponible per nous clients (sense haver de crear una nova carpeta dins de tenants), afegirem la classe a la constant `CORE_CONTEXT_INFO_CHOICES` de `tenants/core/context_info.py`. **En aquest cas no cal crear una carpeta per cada client.**
    - que la API estigui disponible per dos o més clients determinats (i no per la resta), crearem una carpeta dins de `tenants` per cada un dels clients implicats i a dins hi crearem un fitxer `context_info.py` que tingui una constant `CONTEXT_INFO_CHOICES` definida com un iterable de classes que extenen de `ContextInfoAPI`.
- **<APP_SITE_NAME>**: en cas que haguem creat la classe a dins una carpeta de client perquè només ha d'estar disponible per aquest client, afegirem la classe a l'iterable `CONTEXT_INFO_CHOICES`.


## Més info sobre `tenants`
A la carpeta `tenants` hi posarem blocs de codi que només s'hagin d'executar per determinats clients.

Per cada client que hagi de tenir codi propi crearem una carpeta amb el nom d'aquell client (variable d'entorn `APP_SITE_NAME`).

El codi exclusiu de client es pot definir al propi `__init__.py` o en nous fitxers dins de la carpeta de client.

### Com accedir al codi propi de client

**Des del fluxe principal, no farem mai imports que tinguin el nom de client a la ruta**. Ho farem amb les funcions utilitàries definides dins de `tenants/utils.py`.

Per exemple, si creem els següents fitxers:

**`tenants/icgc/__init__.py`**
```python
foo = 'bar'
```

**`tenants/reus/__init__.py`**
```python
foo = 'wow'
```

Al fluxe principal (fora de tenants) podem fer el següent:
```python
from .tenants import import_tenant_attribute
foo = import_tenant_attribute('foo')
print(foo)
```

Al servidor de reus (on `APP_SITE_NAME = 'reus'`) el print mostrarà `wow` mentre que al servidor de l'ICGC (on `APP_SITE_NAME = 'icgc'`) el print mostrarà `bar`. En qualsevol altre servidor, mostrarà `None`.

També podem crear nous fitxers dins la carpeta de client i la manera com hi accedim canviarà lleugerament. Exemple:

**`tenants/icgc/cosetes.py`**
```python
foo = 'bar'
```

**`tenants/reus/cosetes.py`**
```python
foo = 'wow'
```

Al fluxe principal (fora de tenants) podem fer el següent:
```python
from .tenants import import_tenant_attribute
foo = import_tenant_attribute('foo', 'cosetes')
print(foo)
```
El resultat serà el mateix.

La funció `import_tenant_attribute` pot retornar `None` en els següents casos:

- Si no existeix la variable d'entorn `APP_SITE_NAME`.
- Si en un client no hi tenim res (ni la carpeta de client dins de tenants).
- Si en un client tenim carpeta de client però no tenim el mòdul (ex:  `cosetes`) i cridem la funció amb el mòdul (`import_tenant_attribute('foo', 'cosetes')`).
- Si en un client tenim carpeta de client i mòdul, però aquest mòdul no conté l'objecte indicat (ex:  `foo`).

**Exemple:**

**`tenants/icgc/cosetes.py`**
```python
def customize_for_this_tenant(data: Dict) -> Dict:
    ...
    # Manipulem el diccionari data de manera personalitzada pel client
    return data
```

Al fluxe principal:
```python
from .tenants import import_tenant_attribute


def get_data() -> Dict:
    my_data = {'foo': 'bar'}  # Aquest diccionari podria ser un queryset, un model o qualsevol tipus d'objecte de Python o Django.
    customize = import_tenant_attribute('customize_for_this_tenant', 'cosetes')
    if customize:
        my_data = customize(my_data)
    return my_data
```

Aquí, si el client té una carpeta dins de tenants amb un fitxer `cosetes.py` que té una funció `customize_for_this_tenant`, l'executem i en retornem el resultat. Si la funció retorna `None` (per qualsevol dels motius indicats més amunt) retornem els valors per defecte.

### La carpeta core
A la carpeta `tenants/core` hi podem posar codi que pugui ser compartit entre diversos clients.

Per exemple, hi podem definir classes abstractes que centralitzin els atributs bàsics d'una funcionalitat i a dins de cada client crear-hi les classes que l'extenen amb les particularitats de cada client.

### Avantatges

- **Seguretat**. Manté el codi propi de client aïllat dels altres clients en temps d'execució. Des de la app principal el codi dels altres clients no s'executa mai. Un client no pot executar mai codi d'un altre client accidentalment. Per fer-ho cal una acció fraudulenta (veure inconvenients).
- **Manteniment**. Aïlla el codi propi d'un client en l'estructura física del codi (fitxers i carpetes). El fluxe principal no té cap instrucció que sigui exclusiva per un client. Això vol dir que si es deixa de treballar amb un client n'hi ha prou amb esborrar la carpeta de client.
- **Productivitat**. Redueix el temps de desenvolupament i els processos de devops. Com que el codi de diferents clients està al mateix repo, es fa sempre un únic desplegament per tots els clients (tant en desenvolupament com en producció). No cal tenir repos diferents per cada client (com sí que cal en una arquitectura de plugins). El desplegament és sempre el mateix i només cal canviar el valor de la variable d'entorn.

### Inconvenients

- **Seguretat/Privacitat**. Tot i que el codi no és compartit en temps d'execució, sí que està present a tots els servidors. El servidor d'un client té codi d'un altre client. Això vol dir que sí algú accedeix als fitxers del servidor d'un client A pot veure les funcionalitats d'un client B. Això no afectarà al client B, però dóna informació a l'intrús del servidor A (com ara el nom dels clients amb funcionalitats específiques i la lògica d'aquestes funcionalitats).

    Tampoc dóna accés directament a les funcionalitats del client B des del servidor A, però sí que ho pot fer si qui entra modifica el codi o la variable d'entorn. En aquest sentit, és especialment important assegurar les bones pràctiques i no posar mai dades sensibles al codi (tokens, client ids, passwords,...). Així, aquelles funcionalitats de B que depenguin d'alguna mena d'autenticació tampoc es podran fer servir des de A.
