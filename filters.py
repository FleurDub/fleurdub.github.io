"""
Filtres avancés pour l'API REST avec django-filter

QU'EST-CE QU'UN FILTRE ?
Un filtre permet de restreindre les résultats d'une requête API via des
paramètres d'URL (query parameters).

EXEMPLE:
GET /api/pieces/
→ Toutes les pièces

GET /api/pieces/?year_min=1980&year_max=1990
→ Uniquement les pièces entre 1980 et 1990

GET /api/pieces/?designer=yohji-yamamoto&category=jacket
→ Uniquement les jackets de Yohji Yamamoto

DJANGO-FILTER:
django-filter est une bibliothèque qui simplifie la création de filtres
complexes en générant automatiquement les queries SQL.

Sans django-filter (manuel):
pieces = Piece.objects.all()
if 'year_min' in request.GET:
    pieces = pieces.filter(year__gte=request.GET['year_min'])
if 'year_max' in request.GET:
    pieces = pieces.filter(year__lte=request.GET['year_max'])
... (répéter pour chaque filtre)

Avec django-filter (automatique):
class PieceFilter(filters.FilterSet):
    year_min = filters.NumberFilter(field_name='year', lookup_expr='gte')
    year_max = filters.NumberFilter(field_name='year', lookup_expr='lte')

→ Tout est géré automatiquement par django-filter !

AVANTAGES:
- CharFilter            → Texte (name, slug...)
- NumberFilter          → Nombres (year, price...)
- BooleanFilter         → Boolean (is_published, featured)
- DateFilter            → Dates (created_at...)
- UUIDFilter            → UUID (id, foreign keys...)
- ChoiceFilter          → Choix multiples (category, source...)
- RangeFilter           → Fourchette (year_range: 1980-1990)
- MultipleChoiceFilter  → Plusieurs valeurs (categories=dress&categories=jacket)
- Custom Filter         → Logique personnalisée

LOOKUP EXPRESSIONS:
- exact         → Egalité stricte (=)
- iexact        → Egalité insensible à la casse
- contains      → Contient (LIKE '%value%')
- icontains     → Contient insensible casse
- startswith    → Commence par
- endswith      → Finit par
- gt            → Greater than (>)
- gte           → Greater than or equal (>=)
- lt            → Less than (<)
- lte           → Less than or equal (<=)
- in            → Dans une liste
- isnull        → Est NULL
- range         → Entre deux valeurs

FILTRES vs SEARCH:
Filtres (django-filter):
- Champs structurés (year=1980, category=dress)
- Queries exactes et rapides
- Plusieurs filtres combinables

Search (SearchFilter DRF):
- Recherche plein texte (?search=black+dress)
- Cherche dans plusieurs champs
- Moins précis mais plus flexible

Les deux sont complémentaires et utilisés ensemble.

BEST PRATICES APPLIQUEES :
- Validation stricte des inputs
- Noms explicites (year_min au lieu de y_min)
- Méthodes custom pour logique complexe
- Commentaires exhaustifs
- Gestion d'erreurs robuste
- Performance (index BDD sur champs filtrés)
"""
from typing import Optional, List
from django_filters import rest_framework as filters
from django.db.models import Q
from apps.pieces.models import Piece, Category, Era
from apps.designers.models import Designer
import logging

# Logger configuré
logger = logging.getLogger(__name__)

# ════════════════════════════════════════════════════════════════════════════
# FILTRE PRINCIPAL: PieceFilter
# ════════════════════════════════════════════════════════════════════════════

class PieceFilter(filters.FilterSet):
    """
    Filtres avancés pour les pièces de mode

    UTILISATION DANS L'API:
    GET /api/pieces/?year_min=1980&year_max=1990
    GET /api/pieces/?decade=1980
    GET /api/pieces/?designer=yohji-yamamoto
    GET /api/pieces/?category=dress&featured=true
    GET /api/pieces/?source=met&has_materials=true

    CONFIGURATION DANS LE VIEWSET:
    class PieceViewSet(viewsets.ModelViewSet):
        filterset_class = PieceFilter   ← Active tous les filtres
        filter_backends = [DjangoFilterBackend]

    TOUS LES FILTRES SONT COMBINABLES:
    ?year_min=1980&year_max=1990&designer=yohji&category=jacket&featured=true
    → AND entre tous les filtres (pas OR)

    SQL généré:
    WHERE   year >= 1980
    AND     year <= 1990
    AND     designer_slug = 'yohji-yamamoto'
    AND     category_slug = 'jacket'
    AND     featured = True
    """
    # ════════════════════════════════════════════════════════════════════════
    # SECTION 1: FILTRES PAR ANNÉE
    # ════════════════════════════════════════════════════════════════════════

    # Filtre par année (range)
    year_min = filters.NumberFilter(
        field_name='year', 
        # field_name='year' → Filtre le champ 'year' du model Piece

        lookup_expr='gte',
        # lookup_expr='gte' → Greater Than or Equal (>=)
        # SQL généré: WHERE year >= {value}

        label='Année minimum',
        # label affiché dans la documentation OpenAPI

        help_text='Année minimum (incluse). Exemple: 1980'
        # Description dans Swagger UI
        )
    # EXEMPLE:
    # GET /api/pieces/?year_min=1980
    # → Pièces de 1980 et après
    #
    # SQL: SELECT * FROM pieces WHERE year >= 1980
    #
    # VALIDATION:
    # NumberFilter valide automatiquement:
    # - ?year_min=1980      → OK
    # - ?year_min=abc       → HTTP 400 "Enter a number"
    # - ?year_min=1980.5    → HTTP 400 "Enter a whole number"

    year_max = filters.NumberFilter(
        field_name='year', 
        lookup_expr='lte',
        # lookup_expr='lte' → Less Than or Equal (<=)
        # SQL: WHERE year <= {value}

        label='Année maximum',
        help_text='Année maximum (incluse). Exemple: 1990'        
    )
    # EXEMPLE:
    # GET /api/pieces/?year_max=1990
    # → Pièces jusqu'en 1990 inclus
    #
    # COMBINATION:
    # GET /api/pieces/?year_min=1980&year_max=1990
    # → Pièces de la décennie 1980-1990
    #
    # SQL: WHERE year >= 1980 AND year <= 1990

    year = filters.NumberFilter(
        field_name='year',
        lookup_expr='exact',
        # lookup_expr='exact' → Egalité stricte (=)
        # C'est le défaut, on pourrait omettre lookup_expr

        label='Année exacte',
        help_text='Année exacte. Exemple: 1985'   
    )
    # EXEMPLE:
    # GET /api/pieces/?year=1985
    # → Pièces de 1985 uniquement
    #
    # SQL: WHERE year = 1985
    # ATTENTION:
    # Si year_min, year_max ET year sont fournis ensemble,
    # year prend la priorité (plus spécifique)

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 2: FILTRE PAR DÉCENNIE (Logique custom)
    # ════════════════════════════════════════════════════════════════════════

    # Filtre par décennie
    decade = filters.NumberFilter(
        method='filter_decade',
        # method='filter_decade' → Appelle la méthode custom ci-dessous)
        # Au lieu d'un lookup_expr standard

        label='Décennie',
        help_text='Décennie (multiple de 10). Exemple: 1980 pour années 80'
    )

    def filter_decade(self, queryset, name, value):
        """
        Filtre custom pour les décennies

        LOGIQUE:
        decade=1980 → Filtre year >= 1980 AND year < 1990
        decade=1990 → Filtre year >= 1990 AND year < 2000

        POURQUOI UNE METHODE CUSTOM?
        On ne peut pas faire directement avec lookup_expr
        car on doit appliquer DEUX conditions (>= ET <)

        Args:
            queryset (QuerySet):    QuerySet à filtrer
            name (str):             Nom du filtre ('decade')
            value:                  Valeur du paramètre (ex: 1980)

        Returns:
            QuerySet: QuerySet filtré
        
        VALIDATION:
        - Valide que value est un entier
        - Valide que c'est un multiple de 10
        - Valide que c'est dans une plage raisonnable (1800-2100)

        EXEMPLE:
        GET /api/pieces/?decade=1980

        1. value = 1980
        2. Validation: 1980 % 10 == 0
        3. queryset.filter(year__gte=1980, year__lt=1990)
        4. SQL: WHERE year >= 1980 AND year < 1990
        """
        if not value:
            # Paramètre vide → pas de filtre
            return queryset
        
        try:
            decade = int(value)
        except (ValueError, TypeError):
            # Valeur non-entière
            logger.warning(f"filter_decade: Valeur invalide '{value}'")
            return queryset.none()
            # queryset.none() retourne un QuerySet vide
            # Equivalent à: WHERE 1=0
        
        # VALIDATION 1: Multiple de 10
        if decade % 10 != 0:
            logger.warning(
                f"filter_decade: {decade} n'est pas un multiple de 10"
            )
            return queryset.none()
        
        # VALIDATION 2: Plage raisonnable
        if decade < 1800 or decade > 2100:
            logger.warning(
                f"filter_decade: {decade} hors limites (1800-2100)"
            )
            return queryset.none()
        
        # Filtre la décennie
        logger.debug(f"filter_decade: Filtrage décennie {decade}")

        return queryset.filter(
            year__gte=decade,       # year >= 1980
            year__lt=decade + 10    # year < 1990
        )
        # SQL: WHERE year >= 1980 AND year < 1990

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 3: FILTRES PAR DESIGNER
    # ════════════════════════════════════════════════════════════════════════

    designer = filters.CharFilter(
        field_name='designer__slug',
        # Double underscore (__) = traverse la relation ForeignKey
        # designer__slug = Piece.designer.slug

        lookup_expr='iexact',
        # iexact = insensible à la casse
        # 'yohji-yamamoto' == 'Yohji-Yamamoto' == 'YOHJI-YAMAMOTO'

        label='Designer (slug)',
        help_text='Slug du designer. Exemple: yohji-yamamoto'
    )
    # EXEMPLE:
    # GET /api/pieces/?designer=yohji-yamamoto
    # SQL généré:
    # SELECT pieces.ù
    # FROM pieces
    # INNER JOIN designers ON pieces.designer_id = designers.id
    # WHERE LOWER(designers.slug) = LOWER('yohji-yamamoto')
    #
    # PERFORMANCE:
    # - designer__slug a un index (défini dans Designer model)
    # - JOIN automatique optimisé par Django
    # - Query rapide même sur millions de pièces
    
    designer_id = filters.UUIDFilter(
        field_name='designer__id',
        # Filtre par l'UUID du designer
        
        label='Designer (UUID)',
        help_text='UUID du designer' 
    )
    # EXEMPLE:
    # GET /api/pieces/?designer_id=550e8400...
    #
    # UTILITE:
    # - Frontend a l'UUID du designer
    # - Pas besoin de connaître le slug
    # - Plus précis (slug peut théoriquement changer)
    #
    # SQL: WHERE designer.id = '550e8400-...'

    designer_name = filters.CharFilter(
        field_name='designer__name',
        lookup_expr='icontains',
        # icontains = contient, insensible à la casse
        # Cherche "Yohji" dans "Yohji Yamamoto"

        label='Designer (nom)',
        help_text='Nom du designer (partiel OK). Exemple: Yohji'
    )
    # EXEMPLE:
    # GET /api/pieces/?designer_name=Yohji
    # → Toutes les pièces de designers contenant "Yohji"
    #
    # SQL: WHERE designers.name ILIKE '%Yohji%'
    #
    # PERFORMANCE:
    # ILIKE avec % au début est LENT (pas d'index)
    # OK pour recherche occasionnelle
    # Pour recehrche intensive → Utiliser PostgreSQL full-text search

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 4: FILTRES PAR CATÉGORIE
    # ════════════════════════════════════════════════════════════════════════

    category = filters.CharFilter(
        field_name='category__slug',
        lookup_expr='iexact',
        label='Catégorie (slug)',
        help_text='Slug de la catégorie. Exemple: dress'
    )
    # EXEMPLE:
    # GET /api/pieces/?category=dress
    # → Toutes les robes
    #
    # SQL: WHERE categories.slug = 'dress'

    category_id = filters.UUIDFilter(
        field_name='category__id',
        label='Catégorie (UUID)',
        help_text='UUID de la catégorie'
    )

    categories = filters.MultipleChoiceFilter(
        field_name='category__slug',
        # MultipleChoiceFilter accepte plusieurs valeurs

        lookup_expr='in',
        # lookup_expr='in' → SQL IN (...)

        label='Catégories (multiples)',
        help_text='Plusieurs catégories. Exemple: ?categories=dress&categories=jacket'
    )
    # EXEMPLE:
    # GET /api/pieces/?categories=dress&categories=jacket
    # → Toutes les robes OU jackets
    #
    # SQL: WHERE category_slug IN ('dress', 'jacket')
    #
    # C'est un OR, pas un AND !
    # Pour avoir dress ET jacket simultanément → Impossible (une pièce a 1 catégorie)

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 5: FILTRES PAR ÉPOQUE
    # ════════════════════════════════════════════════════════════════════════
    era = filters.CharFilter(
        field_name='era__slug',
        lookup_expr='iexact',
        label='Epoque (slug)',
        help_text='Slug de l\'époque. Exemple: annees-80'
    )
    # EXEMPLE:
    # GET /api/pieces/?era=annees-80
    # → Pièces des annees 80

    era_id = filters.UUIDFilter(
        field_name='era__id',
        label='Epoque (UUID)',
        help_text='UUID de l\'époque'
    )


    # ════════════════════════════════════════════════════════════════════════
    # SECTION 6: FILTRES PAR STATUT
    # ════════════════════════════════════════════════════════════════════════
    
    is_published = filters.BooleanFilter(
        field_name='is_published',
        # BooleanFilter accepte: true, false, 1, 0

        label='Publié',
        help_text='Filtrer par statut de publication. Exemple: ?is_published=true'
    )
    # EXEMPLE:
    # GET /api/pieces/?is_published=true
    # → Pièces publiées
    #
    # GET /api/pieces/?is_published=false
    # → Brouillon (uniquement si user admin)
    #
    # SQL: WHERE is_published = TRUE
    #
    # FORMATS ACCEPTES:
    # - ?is_published=true
    # - ?is_published=True
    # - ?is_published=1
    # - ?is_published=false
    # - ?is_published=False
    # - ?is_published=0

    featured = filters.BooleanFilter(
        field_name='featured',
        label='Mise en avant',
        help_text='Filtrer les pièces featured. Exemple: ?featured=true'
    )
    # EXEMPLE: GET /api/pieces/?featured=true
    # → Pièces featured uniquement
    #
    # SQL: WHERE featured = TRUE

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 7: FILTRES PAR SOURCE
    # ════════════════════════════════════════════════════════════════════════

    source = filters.ChoiceFilter(
        field_name='source',
        # ChoiceFilter = liste de valeurs prédéfinies

        choices=[
            ('manuel', 'Saisie manuelle'),
            ('met', 'Met Museum'),
            ('vogue', 'Vogue Runway'),
            ('vam', 'V&A Museum')
        ],
        # Valeurs autorisées (doivent matcher Piece.source choices)

        label='Source',
        help_text='Source de la pièce. Eemple: ?source=met'
    )
    # EXEMPLE:
    # GET /api/pieces/?source=met
    # → Pièces importées du Met Museum
    #
    # SQL: WHERE source = 'met'
    # 
    # VALIDATION:
    # - ?source=met     → OK
    # - ?source=louvre  → HTTP 400 "Invalid choice"
    # 
    # DOCUMENTATION:
    # OpenAPI génère automatiquement un dropdown avec les choix

    sources = filters.MultipleChoiceFilter(
        field_name='source',
        choices=[
            ('manual', 'Saisie manuelle'),
            ('met', 'Met Museum'),
            ('vogue', 'Vogue Runway'),
            ('vam', 'V&A Museum'),
        ],
        label='SOurces (multiples)',
        help_text='Plusieurs sources. Exemple: ?sources=met&sources=vogue'
    )
    # EXEMPLE:
    # GET /api/pieces/?sources=met&sources=vogue
    # → Pièces du Met Museum OU de Vogue
    # 
    # SQL: WHERE source IN ('met', 'vogue')

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 8: FILTRES PAR SAISON
    # ════════════════════════════════════════════════════════════════════════
    
    season = filters.CharFilter(
        field_name='season',
        lookup_expr='iexact',
        label='Saison',
        help_text='Saison de collection. Exemple: SS25, FW24'
    )

    # EXEMPLE:
    # GET /api/pieces/?season=SS25
    # → Pièces Spring/Summer 2025
    #
    # SQL: WHERE LOWER(season) = LOWER('SS25')

    season_contains = filters.CharFilter(
        field_name='season',
        lookup_expr='icontains',
        label='Saison (partiel)',
        help_text='Recherche partielle dans saison. Exemple: SS'
    )

    # EXEMPLE:
    # GET /api/pieces/?season_contains=SS
    # → Toutes les saisons Spring/Summer
    #
    # SQL: WHERE season ILIKE '%SS%'

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 9: FILTRES PAR MATÉRIAUX (JSONField)
    # ════════════════════════════════════════════════════════════════════════

    has_materials = filters.BooleanFilter(
        method='filter_has_materials',
        # Méthode custom car materials_data est un JSONField

        label='A des matériaux',
        help_text='Filtrer les pièces ayant des matériaux définis'
    )

    def filter_has_materials(self, queryset, name, value):
        """
        Filtre les pièces avant (ou non) des matériaux définis

        LOGIQUE:
        has_materials=true      → materials_data non vide
        has_materials=false     → materials_data vide

        Args:
            queryset:       QuerySet à filtrer
            name:           Nom du filtre
            value (bool):   True ou False
        
        Returns:
            QuerySet filtré
        
        EXEMPLE:
        GET /api/pieces/?has_materials=true
        → Pièces avec matériaux définis

        SQL (PostgreSQL):
        WHERE   materials_data != '[]'::jsonb
        AND     materials_data IS NOT NULL    
        """
        if value is None:
            return queryset
        
        if value:
            # has_materials=true → Matériaux non vide
            return queryset.exclude(
                materials_data=[]
            ).exclude(
                materials_data__isnull=True
            )
        else:
            # has_materials=false → Pas de matériaux
            return queryset.filter(
                Q(materials_data=[]) | Q(materials_data__isnull=True)
            )
    
    material_slug = filters.CharFilter(
        method='filter_material_slug',
        label='Matériau (slug)',
        help_text='Filtre par matériau. Exemple: silk'
    )

    def filter_material_slug(self, queryset, name, value):
        """
        Filtre les pièces contenant un matériau spécifique

        LOGIQUE:
        Cherche dans le JSONField materials_data:
        [{"slug": "silk", "percentage": 70}, ...]

        Args:
            queryset: QuerySet
            name: Nom du filtre
            value: Slug du matériau (ex: "silk")

        Returns:
            QuerySet filtré

        EXEMPLE:
        GET /api/pieces/?material_slug=silk
        → Pièces contenant de la soie

        SQL (PostgreSQL):
        WHERE materials_data @> '[{"slug": "silk"}]'::jsonb

        @> = JSON contains operator (PostgreSQL uniquement)
        """
        if not value:
            return queryset
        
        # PostgreSQL JSON contains
        # Cherche des pièces dont materials_data contient {"slug": "silk"}
        return queryset.filter(
            materials_data__contains=[{'slug': value}]
        )
        # ATTENTION:
        # Nécessite PostgreSQL
        # MySQL n'a pas de JSON contains operator equivalent

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 10: FILTRES PAR COMPTEURS
    # ════════════════════════════════════════════════════════════════════════

    view_count_min = filters.NumberFilter(
        field_name='view_count',
        lookup_expr='gte',
        label='Vues minimum',
        help_text='Nombre de vues minimum. Exemple: 1000'
    )
    # EXEMPLE:
    # GET /api/pieces/?view_count_min=1000
    # → Pièces avec au moins 1000 vues
    #
    # SQL: WHERE view_count >= 1000

    view_count_max = filters.NumberFilter(
        field_name='view_count',
        lookup_expr='lte',
        label='Vues maximum',
        help_text='Nombre de vues maximum'
    )

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 11: FILTRES PAR DATES
    # ════════════════════════════════════════════════════════════════════════

    created_after = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Créé après',
        help_text='Date de création (après). Format: YYYY-MM-DD ou YYYY-MM-DDTHH:MM:SS'
    )
    # EXEMPLE:
    # GET /api/pieces/?created_after=2024-01-01
    # → Pièces créées en 2024
    #
    # SQL: WHERE created_at >= '2024-01-01 00:00:00'
    #
    # FORMATS ACCEPTES§
    # ?created_after=2024-01-01
    # ?created_after=2024-01-01T10:30:00
    # ?created_after=2024-01-01T10:30:00Z
    # ?created_after=2024-01-01T10:30:00+01:00

    created_before = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='Créé avant',
        help_text='Date de création (avant)'
    )

    updated_after = filters.DateTimeFilter(
        field_name='updated_at',
        lookup_expr='gte',
        label='Modifié après',
        help_text='Date de modification (après)'
    )

    updated_before = filters.DateTimeFilter(
        field_name='updated_at',
        lookup_expr='lte',
        label='Modifié avant',
        help_text='Date de modification (avant)'
    )

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 12: FILTRES TEXTUELS AVANCÉS
    # ════════════════════════════════════════════════════════════════════════

    title_contains = filters.CharFilter(
        field_name='title',
        lookup_expr='icontains',
        label='Titre (contient)',
        help_text='Recherche dans le titre. Exemple: black'
    )
    # EXEMPLE:
    # GET /api/pieces/?title_contains=black
    # → Pièces dont le titre contient "black"
    #
    # SQL: WHERE title ILIKE '%black%'
    #
    # DIFFERENCE avec SearchFilter:
    # title_contains: chercher UNIQUEMENT dans title
    # SearchFilter: cherche dans title + description + designer__name 

    title_startswith = filters.CharFilter(
        field_name='title',
        lookup_expr='istartswith',
        label='Titre (commence par)',
        help_text='Titre commençant par. Exemple: Black'
    )

    # EXEMPLE:
    # GET api/pieces/?title_startswith=Black
    # → "Black Coat", "Black Dress"
    # "Little Black Dress" (ne commence pas par Black)
    #
    # SQL: WHERE title ILIKE 'Black%'
    
    description_contains = filters.CharFilter(
        field_name='description',
        lookup_expr='icontains',
        label='Description (contient)',
        help_text='Recherche dans la description'
    )

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 13: FILTRES BOOLÉENS COMBINÉS
    # ════════════════════════════════════════════════════════════════════════

    is_complete = filters.BooleanFilter(
        method='filter_is_complete',
        label='Pièce complète',
        help_text='Filtrer les pièces avec toutes les métadonnées remplies'
    )

    def filter_is_complete(self, queryset, name, value):
        """
        Filtre les pièces "complètes" (toutes métadonnées remplies)

        CRITERES DE COMPLETUDE:
        - Titre présent
        - Description présente
        - Image présente
        - Catégorie définie
        - Matériaux définis

        Args:
            queryset: QuerySet
            name: Nom du filtre
            value (bool): True ou False

        Returns:
            QuerySet filtré
        
        EXEMPLE:
        GET /api/pieces/?is_complete=true
        → Pièces avec toutes les métadonnées

        SQL:
        WHERE title != ''
            AND description != ''
            AND image != ''
            AND category_id IS NOT NULL
            AND materials_data != '[]'
        """
        if value is None:
            return queryset
        
        if value:
            # Pièces complètes
            return queryset.exclude(
                title=''
            ).exclude(
                description=''
            ).exclude(
                image=''
            ).exclude(
                category__isnull=True
            ).exclude(
                materials_data=[]
            )
        else:
            # Pièces incomplètes (au moins un champ manquant)
            return queryset.filter(
                Q(title='') |
                Q(description='') |
                Q(image='') |
                Q(category__isnull=True) |
                Q(materials_data=[])
            )

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 14: NOUVEAUX FILTRES - MEMORA v2
    # ════════════════════════════════════════════════════════════════════════
    
    maison = filters.CharFilter(
        field_name='designer__maison__slug',
        lookup_expr='iexact',
        label='Maison (slug)',
        help_text='Filtre par maison. Exemple: ?maison=balmain'
    )

    collection = filters.CharFilter(
        field_name='collection__slug',
        lookup_expr='iexact',
        label='Collection (slug)',
        help_text='Filtre par collection. Exemple: ?collection=new-look-ss1947'
    )

    technique = filters.CharFilter(
        field_name='techniques__slug',
        lookup_expr='iexact',
        label='Technique (slug)',
        help_text='Filtre par technique. Exemple: ?technique=plisse-fortuny'
    )

    has_fragments = filters.BooleanFilter(
        method='filter_has_fragments',
        label='A des fragments approuvés',
        help_text='?has_fragments=true - pièces avec au moins un fragment approuvé'
    )

    def filter_has_fragments(self, queryset, name, value):
        if value is None:
            return queryset
        if value:
            return queryset.filter(
                fragements__status__in=['approuved', 'edited']
            ).distinct()
        return queryset.exclude(
            fragments__statys__in=['approuved', 'edited']
        ).destinct()

    dominant_signal = filters.CharFilter(
        method='filter_dominant_signal',
        label='Signal dominant',
        help_text='?dominant_signal=a|b|c - filtre par signal dominant du scoring'
    )

    def filter_dominant_signal(self, queryset, name, value):
        if value not in ['a', 'b', 'c']:
            return queryset
        return queryset.filter(
            proximity_data__dominant_signal=value
        )
    
    proximity_min = filters.NumberFilter(
        method='filter_proximity_min',
        label='Score de proximité minimum',
        help_text='?proximity_min=12 - pièces avec au moins une résonance >= ce score'  
    )

    def filter_proximity_min(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            proximity_data__total__gte=value
        )
        
    # ════════════════════════════════════════════════════════════════════════
    # META CONFIGURATION
    # ════════════════════════════════════════════════════════════════════════ 

    class Meta:
        model = Piece
        # Model sur lequel s'appliquent les filtres

        fields = []
        # fields = [] car on définit tout manuellement ci-dessus
        # 
        # ALTERNATIVE (génération automatique):
        # fields = ['year', 'category', 'designer']
        # → django-filter génère automatiquement des filtres basiques
        # 
        # Mais on préfère définir manuellement pour:
        # - Contrôle total (lookup_expr, validation...)
        # - Noms explicites (year_min au lieu de year__gte)
        # - Méthodes custom
        # - Documentation claire   



# ════════════════════════════════════════════════════════════════════════════
# FILTRES SUPPLÉMENTAIRES: DesignerFilter
# ════════════════════════════════════════════════════════════════════════════

class DesignerFilter(filters.FilterSet):
    """
    Filtres pour les designers

    UTILISATION:
    GET /api/designers/?nationality=japanese
    GET /api/designers/?birth_year_min=1940
    GET /api/designers/?has_maison=true
    """

    # ════════════════════════════════════════════════════════════════════════
    # FILTRES PAR NATIONALITÉ
    # ════════════════════════════════════════════════════════════════════════

    nationality = filters.CharFilter(
        field_name='nationality',
        lookup_expr='iexact',
        label='Nationalité',
        help_text='Nationalité exacte. Exemple: Japanese'
    )
    # EXEMPLE:
    # GET /api/designers/?nationality=Japanese
    # → Designers japonais

    nationality_contains = filters.CharFilter(
        field_name='nationality',
        lookup_expr='icontains',
        label='Nationalité (partiel)',
        help_text='Recherche partielle. Exemple: Japan'
    )

    # ════════════════════════════════════════════════════════════════════════
    # FILTRES PAR ANNÉE DE NAISSANCE
    # ════════════════════════════════════════════════════════════════════════

    birth_year_min = filters.NumberFilter(
        field_name='birth_year',
        lookup_expr='gte',
        label='Né après',
        help_text='Année de naissance minimum'
    )

    birth_year_max = filters.NumberFilter(
        field_name='birth_year',
        lookup_expr='lte',
        label='Né avant',
        help_text='Année de naissance manimum'
    )

    # ════════════════════════════════════════════════════════════════════════
    # FILTRES PAR MAISON
    # ════════════════════════════════════════════════════════════════════════
    
    maison = filters.CharFilter(
        field_name='maison__slug',
        lookup_expr='iexact',
        label='Maison (slug)',
        help_text='Slug de la maison. Exemple: chanel'
    )

    maison_id = filters.UUIDFilter(
        field_name='maison__id',
        label='Maison (UUID)',
        help_text='UUID de la maison'
    )

    has_maison = filters.BooleanFilter(
        method='filter_has_maison',
        label='A une maison',
        help_text='Filtrer les designers avec/sans maison'
    )

    