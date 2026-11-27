with reelle as (
    select
        voiture_id,
        sum(carburant_l) * 100 / sum(distance_km)
            as conso_reelle_l100,
        count(*) as nb_trajets
    from {{ ref('stg_trajets') }}
    group by 1
)

select
    v.modele,
    v.origine,
    v.annee,
    sum(r.nb_trajets) as nb_trajets,
    cast(avg(v.conso_annoncee_l100)
        as decimal(6, 2)) as conso_annoncee_l100,
    cast(avg(r.conso_reelle_l100)
        as decimal(6, 2)) as conso_reelle_l100,
    cast(100 * (
        avg(r.conso_reelle_l100)
        / avg(v.conso_annoncee_l100) - 1
    ) as decimal(6, 1)) as ecart_pct
from reelle r
join {{ ref('stg_voitures') }} v using (voiture_id)
group by 1, 2, 3