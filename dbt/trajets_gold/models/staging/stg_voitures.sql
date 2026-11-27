select
    id_voiture as voiture_id,
    nom as modele,
    annee,
    origine,
    conso_l100 as conso_annoncee_l100
from {{ source('silver', 'voitures') }}