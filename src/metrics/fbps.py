import numpy as np


def compute_vi(balance, estimated_salary):
    return 0.05 * balance + 0.01 * estimated_salary


def fbps_score(
    y_true,
    y_pred,
    balances,
    estimated_salaries,
    Cret=20,
    p_success=1.0,
):
    """
    Calcul de la métrique FBPS.

    Paramètres
    ----------
    y_true : array-like, étiquettes réelles (0/1)
    y_pred : array-like, prédictions (0/1)
    balances : array-like, soldes clients
    estimated_salaries : array-like, salaires estimés clients
    Cret : float, coût fixe de rétention par client ciblé
    p_success : float, probabilité de succès de l'action de rétention

    Retourne
    --------
    float : score FBPS (gain net de la stratégie de rétention)
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    balances = np.asarray(balances)
    estimated_salaries = np.asarray(estimated_salaries)

    V = compute_vi(balances, estimated_salaries)

    tp_mask = (y_true == 1) & (y_pred == 1)
    fp_mask = (y_true == 0) & (y_pred == 1)
    fn_mask = (y_true == 1) & (y_pred == 0)

    gain_tp = np.sum(V[tp_mask] * p_success - Cret)
    cost_fp = np.sum(-Cret * np.ones(np.sum(fp_mask)))
    loss_fn = np.sum(-V[fn_mask])

    return gain_tp + cost_fp + loss_fn