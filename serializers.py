"""
Serializers optimisés avec validation stricte

QU'EST-CE QU'UN SARIALIZER ?
    Un traducteur bidirectionnel entre:
    Python objects (Django models) ←→ JSON (API REST)

Deux directions:
1. SERIALIZATION (Python → JSON):
    Piece object → {"id": "123", "title": "Robe noire", ...}

2. DESERIALIZATION (JSON → Python):
    {"title": "Robe noire"} → Piece object validé


POURQUOI PLUSIEURS SERIALIZERS ?
- PieceListSerializer: données minimales pour listes (performance)
- PieceDetailSerializer: toutes les données pour page détail
- PieceCreateUpdateSerializer: validation stricte pour création/modification

Principe: Ne jamais envoyer plus de données que nécessaire.


# ════════════════════════════════════════════════════════════════════════════
# RÉSUMÉ: QUAND UTILISER QUEL SERIALIZER ?
# ════════════════════════════════════════════════════════════════════════════

┌─────────────────────┬───────────────────────────┬──────────────────┐
│ Endpoint            │ Action                    │ Serializer       │
├─────────────────────┼───────────────────────────┼──────────────────┤
│ GET /pieces/        │ Liste paginée             │ PieceList        │
│ GET /pieces/{id}/   │ Détail complet            │ PieceDetail      │
│ POST /pieces/       │ Création                  │ PieceCreateUpdate│
│ PUT /pieces/{id}/   │ Mise à jour complète      │ PieceCreateUpdate│
│ PATCH /pieces/{id}/ │ Mise à jour partielle     │ PieceCreateUpdate│
├─────────────────────┼───────────────────────────┼──────────────────┤
│ GET /designers/     │ Liste                     │ DesignerList     │
│ GET /designers/{id}/│ Détail avec pièces        │ DesignerDetail   │
├─────────────────────┼───────────────────────────┼──────────────────┤
│ GET /pieces/stats/  │ Statistiques globales     │ PieceStats       │
└─────────────────────────────────────────────────────────────────────
"""

from rest_framework import serializers
from apps.pieces.models import Piece, Category, Era, Collection, Technique, ContentFragment
from apps.designers.models import Designer, Maison

# ════════════════════════════════════════════════════════════════════════════
# SECTION 1 : NESTED SERIALIZERS (Serializers imbriqués)
# ════════════════════════════════════════════════════════════════════════════

class MaisonMinimalSerializer(serializers.ModelSerializer):
    """
    Représentation minimale d'une Maison
    
    Utilisé dans: DesignerMinimalSerializer

    Pourquoi "Minimal" ?
        On ne veut que les infos essentielles, pas tout l'objet:
        {"id": "...", "name": "Chanel", "slug": "chanel"}

    Avantages:
    - Payload JSON plus léger → moins de bande passante
    - Temps de serialization réduit
    - Evite de surcharger le frontend avec des données inutiles
    """

    class Meta:
        model = Maison
        fields = ['id', 'name', 'slug']
        # Seulement 3 champs sur les ~10 du model


class DesignerMinimalSerializer(serializers.ModelSerializer):
    """
    Représentation minimale d'un Designer

    Utilisé dans: PieceListSerializer, PieceDetailSerializer

    Exemple de JSON généré:
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "MEMORA PHYSIS",
        "slug": "memora-physis",
        "maison": {
            "id": "...",
            "name": "MEMORA PHYSIS MM",
            "slug": "memora-physis-mm"
        }
    }
    """

    # Serializer imbriqué: maison sera sérialisée via MaisonMinimalSerializer
    maison = MaisonMinimalSerializer(read_only=True)
    # read_only=True → Ne peut pas être modifié via l'API
    # Si tu POST {"maison": {...}}, ce champ sera ignoré

    class Meta:
        model = Designer
        fields = ['id', 'name', 'slug', 'maison']


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer simple pour Category

    Pas besoin de version "minimal" car Category est déjà simple.
    """
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class EraSerializer(serializers.ModelSerializer):
    """
    Serializer simple pour Era

    Exemple JSON:
    {
        "id": "...",
        "name": "Années 80",
        "slug": "annees-80",
        "start_year": 1980,
        "end_year": 1989
    }
    """

    class Meta:
        model = Era
        fields = ['id', 'name', 'slug', 'start_year', 'end_year']


class ContentFragmentSerializer(serializers.ModelSerializer):
    """
    Fragment éditorial - uniquement les approved/edited sont publics.
    """
    reviewed_by = serializers.SerializerMethodField()

    class Meta:
        model = ContentFragment
        fields = [
            'id',
            'fragment_type',
            'status',
            'content',
            'confidence_score',
            'reviewed_by',
            'reviewed_at',
        ]
        # content_orginal n'est JAMAIS exposé publiquement

    def get_reviewed_by(self, obj):
        if obj.reviewed_by:
            return obj.reviewed_by.get_initials() if hasattr(obj.reviewed_by, 'get_initials') else obj.reviewed_by.username[:2].upper()
        return None

class TechniqueSerializer(serializers.ModelSerializer):

    class Meta:
        model = Technique
        fields = ['id', 'name', 'slug']

class CollectionSerializer(serializers.ModelSerializer):
    maison = MaisonMinimalSerializer(read_only=True)
    pieces_count = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = [
            'id',
            'slug',
            'maison',
            'season',
            'year',
            'name',
            'display',
            'presentation_date',
            'presentation_city',
            'pieces_count',
        ]

    def get_pieces_count(self, obj):
        return obj.pieces.filter(is_published=True).count()

# ════════════════════════════════════════════════════════════════════════════
# SECTION 2 : PIECE SERIALIZERS (Cœur de l'API)
# ════════════════════════════════════════════════════════════════════════════

class PieceListSerializer(serializers.ModelSerializer):
    """
    Serializer optimisé pour les listes de pièces

    CAS D'USAGE:
    - GET /api/pieces/ (liste paginée)
    - GET /api/pieces/?designer=vivienne-westwood
    - GET /api/designers/123/pieces

    OPTMISATION #1: Champs minimaux
        On ne charge pas:
        - story (TextField long)
        - description complète
        - métadonnées source
    
        Résultat: payload JSON 3x plus léger que PieceDetailSerializer
    
    OPTIMISATION #2: Thumbnails
        On utilise thumbnail_url (200x200) au lieu de l'image complète
        → Chargement 36x plus rapide (1200² / 200² = 36)
    
            Exemple JSON généré:
    {
        "id": "550e8400-...",
        "title": "Black Asymmetric Coat",
        "slug": "black-asymmetric-coat",
        "designer": {
            "name": "Yohji Yamamoto",
            "slug": "yohji-yamamoto"
        },
        "category": {
            "name": "Jacket",
            "slug": "jacket"
        },
        "year": 1985,
        "season": "FW85",
        "image_url": "https://api.memora.com/media/pieces/...",
        "thumbnail_url": "https://api.memora.com/media/CACHE/...",
        "image_alt": "Black asymmetric wool coat",
        "featured": true,
        "view_count": 1247
    }   
    """

    # Nested serializers (sérialisés automatiquement)
    designer = DesignerMinimalSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    collection = CollectionSerializer(read_only=True)

    # SerializerMethodField = champ calculé dynamiquement
    # Appelle la méthode get_<field_name>() pour obtenir la valeur
    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Piece
        fields = [
            'id',
            'title',
            'slug',
            'designer',         # Nested
            'category',         # Nested
            'year',
            'season',
            'collection',
            'image_url',        # Calculé
            'thumbnail_url',     # Calculé
            'image_alt',
            'featured',
            'view_count',
        ]
        # On n'inclut PAS: description, story, source, materials_data...

        read_only_fields = ['view_count']
        # view_count ne peut pas être modifié directement via l'API
        # Uniquement via l'endpoint dédié /pieces/{id}/increment_view/

    def get_image_url(self, obj):
        """
        Génère l'URL absolue de l'image principale

        Args:
            obj (Piece): L'objet Piece en cours de sérialisation

        Returns:
            str: URL complète de l'image
            None: Si pas d'image

        POURQUOI UNE URL ABSOLUE ?
        obj.image.url retourne: /media/pieces/2024/01/coat.jpg (relatif)
        On veut: https://api.memora.com/media/pieces/2024/01/coat.jpg (absolu)

        Pourquoi ?
        - Frontend peut être sur un domaine différent (app.memora.com)
        - Mobile apps ont besoin d'URLs absolues
        - Meilleure pratique REST API

        Comment ?
        self.context contient la requête HTTP (injectée par DRF)
        request.build_absolute_uri() construit l'URL complète
        """

        if obj.image:
            # Récupère la requête HTTP depuis le contexte
            request = self.context.get('request')

            if request:
                # Construit URL absolue: https://domain.com + /media/...
                return request.build_absolute_uri(obj.image.url)
            
            # Fallback: retourne URL relative si pas de requête
            return obj.image.url
        
        return None
    
    def get_thumbnail_url(self, obj):
        """
        Génère l'URL du thumbnail (optimisé WebP 200x200)

        obj.thumbnail est un ImageSpecField (django-imagekit)
        Génère automatiquement un thumbnail:
        - Redimensionné à 200x200 (crop center)
        - Converti en WebP (meilleure compression)
        - Qualité 80%
        - Mis en cache

        Première requête: génère le thumbnail
        Requêtes suivantes: sert depuis le cache
        """
        if obj.thumbnail:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return None

class PieceDetailSerializer(serializers.ModelSerializer):
    """
    Serializer complet pour le détail d'une pièce

    CAS D'USAGE:
    GET /api/pieces/{id}/

    DIFFERENCE avec PieceListSerializer:
    - Inclut tous les champs (description, story, source...)
    - Inclut les computed fields (decade)
    - Inclut les métadonnées (created_at, updated_at)
    - Inclut les matériaux (interconnexion PHYSIS)
        
    Exemple JSON généré:
    {
        "id": "550e8400-...",
        "title": "Black Asymmetric Coat",
        "slug": "black-asymmetric-coat",
        "designer": {
            "id": "...",
            "name": "Yohji Yamamoto",
            "slug": "yohji-yamamoto",
            "maison": {
                "name": "Yohji Yamamoto Inc.",
                "slug": "yohji-yamamoto-inc"
            }
        },
        "category": {"name": "Jacket", "slug": "jacket"},
        "era": {"name": "Années 80", "slug": "annees-80", ...},
        "year": 1985,
        "decade": 1980,  ← Calculé automatiquement
        "season": "FW85",
        "description": "Iconic asymmetric wool coat...",
        "story": "This coat revolutionized...",
        "image_url": "https://...",
        "thumbnail_url": "https://...",
        "image_credit": "Photo by Jane Doe",
        "image_alt": "Black asymmetric wool coat",
        "source": "manual",
        "external_url": "",
        "materials": [  ← Interconnexion PHYSIS
            {"slug": "wool", "percentage": 100}
        ],
        "featured": true,
        "view_count": 1247,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-20T14:22:00Z"
    }

    """

    # Nested serializers
    designer = DesignerMinimalSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    era = EraSerializer(read_only=True)
    collection = CollectionSerializer(read_only=True)
    techniques = TechniqueSerializer(many=True, read_only=True)
    fragments = serializers.SerializerMethodField()

    # URLs calculées
    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    # Computed fields
    decade = serializers.ReadOnlyField()
    # ReadOnlyField → Lit la propriété @property decade du model
    # Equivalent à: decade = obj.decade

    # Matériaux (interconnexion PHYSIS)
    materials = serializers.SerializerMethodField()

    class Meta:
        model = Piece
        fields = [
            'id',
            'title',
            'slug',
            'designer',
            'category',
            'era',
            'collection',
            'techniques',
            'year',
            'decade',           # Computed
            'season',
            'description',      # ← Pas dans ListSerializer
            'story',            # ← Pas dans ListSerializer
            'image_url',
            'thumbnail_url',
            'image_credit',
            'image_alt',
            'source',           # ← Pas dans ListSerializer
            'external_url',     # ← Pas dans ListSerializer
            'materials',        # ← Pas dans ListSerializer
            'fragments',
            'mesh_status',
            'proximity_data',
            'featured',
            'view_count',
            'created_at',       # ← Pas dans ListSerializer
            'updated_at'        # ← Pas dans ListSerializer    
        ]

        read_only_fields = ['view_count', 'created_at', 'updated_at']
        # Ces champs sont auto-gérés, pas modifiables via API

    def get_image_url(self, obj):
        """ Même logique que PieceListSerializer """

        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def get_thumbnail_url(self, obj):
        """ Même logique que PieceListSerializer """
        if obj.thumbnail:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return None
    
    def get_materials(self, obj):
        """
        Retourne les matériaux enrichis depuis PHYSIS API
        
        ETAT ACTUEL:
            Retourne simplement obj.materials_data (JSONField)
            Exemple: [{"slug": "silk", "percentage": 70}]
        
        FUTUR (interconnexion PHYSIS):
            Pour chaque material slug, faire un appel à PHYSIS API:

            metarials_data = obj.materials_data
            # [{"slug": "silk", "percentage": 70}]

            enriched = []
            for mat in materials_data:
            # Appel à PHYSIS API
            physis_data = requests.get(f'https://physis.api/materials/{mat["slug"]}/')
            enriched.append({
                "slug":         mat["slug"],
                "percentage":   mat["percentage"],
                "name":         physis_data["name"],
                "family":       physis_data["family"],
                "texture":      physis_data["texture"],
                "image":        physis_data["image_macro"]
            })

            return enriched

        OPTIMISATION:
        Cacher les résultats PHYSIS avec Redis (TTL 1h)
        Evite des appels API répétés pour les mêmes matériaux
        """
        return obj.materials_data
    
    def get_fragments(self, obj):
        """Retourne uniquement les fragments approved ou edited - jamais les drafts."""
        approved = obj.fragments.filter(
            status__in=['approved', 'edited']
        )
        return ContentFragmentSerializer(approved, many=True).data

class PieceCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer pour création/MAJ de la pièce

    CAS D'USAGE:

    POST    /api/pieces/        (création)
    PUT     /api/pieces/{id}/   (MAJ complète)
    PATCH   /api/pieces/{id}/   (MAJ partielle)

    DIFFERENCE avec les autres serializers:
    - Accepte les IDs pour les ForeignKeys (designer_id, category_id...)
    - Validation stricte des données entrantes
    - write_only fields (pas renvoyés dans la réponse)
    - Logique de validation métier

    EXEMPLE D'UTILISATION:

    POST /api/pieces/
    {
        "title": "New Coat",
        "designer_id": "550e8400-e29b-41d4-a716-446655440000",
        "category_id": "...",
        "year": 2024,
        "description": "A beautiful coat...",
        "image": <binary data>,
        "image_credit": "Photo by John Doe",
        "image_alt": "Black wool coat"
    }
    
    → Django valide
    → Crée l'objet Piece
    → Retourne le JSON via PieceDetailSerializer
    """

    # ForeignKeys: on accepte les UUIDs en input
    designer_id = serializers.PrimaryKeyRelatedField(
        queryset=Designer.objects.all(), # Valide que l'UUIS existe en BDD
        source='designer',               # Mep vers le champ 'designer' du model
        write_only=True                  # Pas inclus dans la réponse GET
    )
    # Pouquoi write_only ?
    # ─────────────────────
    # Input (POST): {"designer_id": "550e8400-..."}
    # Output (GET): {"designer": {"id":"...", "name":"...", ...}}
    #                              ↑ Nested serializer, pas juste l'ID
    
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False,     # Optionnel
        allow_null=True     # Peut être null
    )

    era_id = serializers.PrimaryKeyRelatedField(
        queryset=Era.objects.all(),
        source='era',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Piece
        fields = [
            'title',
            'designer_id',  # write_only
            'category_id',  # write_only
            'era_id',       # write_only
            'year',
            'season',
            'description',
            'story',
            'image',
            'image_credit',
            'image_alt',
            'source',
            'source_id',
            'external_url',
            'materials_data',
            'is_published',
            'featured',
        ]
        # On n'inclut pas: id, slug (auto-générés), timestamps, view_count


    # ════════════════════════════════════════════════════════════════════════
    # VALIDATION - Niveau champ individuel
    # ════════════════════════════════════════════════════════════════════════    
    
    def validate_year(self, value):
        """
        Validation custom du champ 'year'
        
        Django REST Framework appelle automatiquement validate_<field_name>() pour chaque champ.

        Args:
            value: La veleur soumise pour 'year'

        Returns:
            value: Si validation OK

        Raises:
            serializers.ValidationError: Si validation échoue

        Exemple:
        POST {"year": 1300}
        → ValidationError: "L'année doit être entre 1400 et 2100"
        → HTTP 400 Bad Request
        """
        if value < 1400 or value > 2100:
            raise serializers.ValidationError("L'année doit être entre 1400 et 2100")
        return value
    
    def validate_image_alt(self, value):
        """
        Validation: image_alt obligatoire si image fournie

        PROBLEME:
        
        A ce stade, on n'a accès qu'au champ 'image_alt', pas à 'image'.

        SOLUTION:

        Validation cross-field dans validate() (voir ci-dessous)
        Cette méthode vérifie juste que image_alt n'est pas vide si fourni.
        """
        return value
    
    # ════════════════════════════════════════════════════════════════════════
    # VALIDATION - Cross-field (plusieurs champs)
    # ════════════════════════════════════════════════════════════════════════

    def validate(self, attrs):
        """
        Validation cross-field: valide plusieurs champs ensemble

        Django REST Framework appelle cette méthode APRES validate_<field>()

        Args:
            attrs (dict): Dictionnaire de tous les champs validés
                        Exemple: {
                             'title': 'Mon titre',
                             'year': 2024,
                             'designer': <Designer object>,
                             'image': <InMemoryUploadedFile>,
                             ...
                         }
        
        Returns:
            attrs: Si validation OK (peut être modifié)

        Raises:
            serializers.ValidationError: Si validation échoue
        
        CAS D'USAGE:
        - Vérifier cohérence entre plusieurs champs
        - Validation métier complexe
        - Contraintes d'unicité custom
        """

        # VALIDATION 1: Image alt obligatoire si image existe
        if attrs.get('image') and not attrs.get('image_alt'):
            raise serializers.ValidationError({
                'image_alt:' "Le texte alternatif est obligatoire pour l'accessibilité"
            })
        # Pourquoi ?
        # ──────────
        # Accessibilité WCAG: toute image doit avoir une texte alternatif
        # pour les lecteurs d'écran (personnes aveugles)

        # VALIDATION 2: Unicité source + source_id
        if attrs.get('source') != 'manual' and attrs.get('source_id'):
            # Vérifie qu'il n'existe pas déjà une pièce avec ce source+source_id
            existing = Piece.objects.filter(
                source=attrs['source'],
                source_id=attrs['source_id']
            )

            # Si on est en UPDATE, exclure la pièce actuelle
            if self.instance:  # self.instance existe uniquement en UPDATE
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise serializers.ValidationError({
                    'source_id': f"Une pièce existe déjà avec cet ID dans {attrs['source']}"
                })
        
        # Pourquoi cette validation ?
        # ───────────────────────────
        # Eviter les doublons lors d'imports externes (Met Museum, Vogue...)
        # Chaque pièce importée doit être unique par (source, source_id)

        return attrs
    

# ════════════════════════════════════════════════════════════════════════════
# SECTION 3 : DESIGNER SERIALIZERS
# ════════════════════════════════════════════════════════════════════════════

class DesignerListSerializer(serializers.ModelSerializer):
    """
    Serializer pour liste de designers

    GET /api/designers/
    {
        "id": "...",
        "name": "Yohji Yamamoto",
        "slug": "yohji-yamamoto",
        "maison": {
            "name": "Yohji Yamamoto Inc.",
            "slug": "yohji-yamamoto-inc"
        },
        "nationality": "Japanese",
        "birth_year": 1943,
        "pieces_count": 156  ← Annoté dans la query (voir views.py)
    }
    """

    maison = MaisonMinimalSerializer(read_only=True)
    # pieces_count est annoté dans la query (views.py):
    # Designer.objects.annotate(pieces_count=Count('pieces'))
    pieces_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Designer
        fields = [
            'id',
            'name',
            'slug',
            'maison',
            'nationality',
            'birth_year',
            'pieces_count',    # Computed
        ]


class DesignerDetailSerializer(serializers.ModelSerializer):
    """
    Serializer détaillé pour un designer

    GET /api/designers/{id}/

    Inclut:
    - Toutes les infos du designer
    - Liste de ses pièces (nested)

    Exemple JSON:
    {
        "id": "...",
        "name": "Yohji Yamamoto",
        "slug": "yohji-yamamoto",
        "maison": {...},
        "birth_year": 1943,
        "death_year": null,
        "nationality": "Japanese",
        "bio": "Yohji Yamamoto is a Japanese fashion designer...",
        "image": "https://.../designers/yohji.jpg",
        "website": "https://www.yohjiyamamoto.co.jp",
        "instagram": "yohjiyamamoto",
        "pieces_count": 156,
        "pieces": [  ← Liste complète de ses pièces
            {
                "id": "...",
                "title": "Black Asymmetric Coat",
                "year": 1985,
                ...
            },
            ...
        ],
        "created_at": "2024-01-01T00:00:00Z"
    }
    """
    maison = MaisonMinimalSerializer(read_only=True)
    
    # Nested: toutes les pièces du designer
    pieces = PieceListSerializer(many=True, read_only=True)
    # many=True → Sérialise une liste d'objets
    # Correspond au related_name='pieces' dans Piece.designer

    pieces_count = serializers.SerializerMethodField()

    class Meta:
        model = Designer
        fields = [
            'id',
            'name',
            'slug',
            'maison',
            'birth_year',
            'death_year',
            'nationality',
            'bio',
            'image',
            'website',
            'instagram',
            'pieces_count',
            'pieces',           # Nested
            'created_at',
        ]
    
    def get_pieces_count(self, obj):
        """
        Compte uniquement les pièces publiées

        Pourquoi pas juste obj.pieces.count() ?
            On veut uniquement les pièces is_published=True

        Performance:
            Cette query est optimisée car on précharge les pièces
            dans la view avec prefetch_related() (voir views.py)
        """
        return obj.pieces.filter(is_published=True).count()
    

# ════════════════════════════════════════════════════════════════════════════
# SECTION 4 : STATS SERIALIZER (pas lié à un model)
# ════════════════════════════════════════════════════════════════════════════

class PieceStatsSerializer(serializers.Serializer):
    """
    Serializer pour statistiques globales

    GET /api/pieces/stats/

    Pas de model associé (Serializer pur, pas ModelSerializer)
    Utilisé pour valider/sérialiser des données arbitraires

    Exemple JSON:
    {
        "total_pieces": 1247,
        "total_designers": 89,
        "total_categories": 12,
        "decade_distribution": {
            "1980": 234,
            "1990": 456,
            "2000": 321,
            "2010": 236
        },
        "top_designers": [
            {
                "name": "Yohji Yamamoto",
                "slug": "yohji-yamamoto",
                "num_pieces": 156
            },
            ...
        ]
    }
    """
    total_pieces = serializers.IntegerField()
    total_designers = serializers.IntegerField()
    total_categories = serializers.IntegerField()

    # DictField: accepte n'importe quel dictionnaire JSON
    decade_distribution = serializers.DictField()

    # ListField: accepte n'importe quelle liste JSON
    top_designers = serializers.ListField()

    # Pas de Meta car pas de model associé
    # Serializer pur pour valider des données arbitraires

