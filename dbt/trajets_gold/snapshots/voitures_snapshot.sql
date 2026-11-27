{% snapshot voitures_snapshot %}

{{ config(
    target_schema='snapshots',
    unique_key='voiture_id',
    strategy='check',
    check_cols=['origine', 'conso_annoncee_l100']
) }}

select
    voiture_id,
    modele,
    origine,
    conso_annoncee_l100
from {{ ref('stg_voitures') }}

{% endsnapshot %}