with source as (
    select * from {{ source('silver', 'trajets') }}
),

renomme as (
    select
        id_trajet as trajet_id,
        id_voiture as voiture_id,
        conducteur as conducteur_id,
        jour,
        debut as debut_a,
        ville,
        type_route,
        distance_km,
        duree_min,
        cast(carburant_l as decimal(10, 2)) as carburant_l
    from source
)

select * from renomme