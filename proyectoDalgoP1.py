"""
Diseno y Analisis de Algoritmos 2025-20
Problema 1

- Santiago Rodriguez Mora - 202110332
- Valeria Torres Gomez - 202110363

Descripción de la solución:
  Dado k, n y pesos p0,p1,p2,p3,p4 para columnas,
  encontrar el puntaje de creatividad máximo al repartir n en k celdas.
  Puntúan solo dígitos 3/6/9: en la columna p, 3->1*P[p], 6->2*P[p], 9->3*P[p].
  Se resuelve con DP por columnas en base 10.
Entrada:
  T casos -> para cada caso: k n p0 p1 p2 p3 p4
Salida:
  Una línea -> por caso con el máximo puntaje
"""

import sys

NEG_INF = -10**30


def to_digits_base10(n: int):
    """
    Convierte un entero n en su representación por columnas (base 10),
    devolviendo una lista de dígitos [n0, n1, n2, ...] donde
        - n0 son las unidades,
        - n1 las decenas,
        - n2 las centenas,
        - n3 los miles,
        - n4 los diez miles

    Args:
        n (int): Suma total a representar por columnas.
    Returns:
        List[int]: Lista de dígitos en base 10 con el orden de derecha a izquierda,
                   primero unidades, luego decenas, etc. Si n = 0, retorna [0].
    """
    if n == 0:
        return [0]
    digs = []
    while n > 0:
        digs.append(n % 10)
        n //= 10
    return digs


def cap_decenas_global(k: int) -> int:
    """
    Cota global razonable de “decenas que pueden llegar” a cualquier columna.

    Justificación: en una columna s_p ≤ 9k, lo que equivale a ≈ (9k)/10 decenas.
    Se agrega un pequeño margen para cubrir bordes.

    Retorna:
        Entero CMAX.
    """
    return (9 * k) // 10 + 2


def cap_decenas_por_columna(p: int, k: int, cmax_global: int) -> int:
    """
    Cota más apretada para “decenas que pueden llegar” a la columna p.

    Intuición práctica: con p columnas a la derecha ya sumadas, como mucho
    han podido “viajar” ≈ p*(9k)/10 decenas. Esto reduce el tamaño del DP por nivel.

    Retorna:
        Límite superior entero para c en la columna p.
    """
    return min(cmax_global, (p * (9 * k)) // 10 + 2)


def rango_csig_valido(c_llegan: int, n_p: int, k: int, c_sig_lim: int) -> Tuple[int, int]:
    """
    Dado c (decenas que llegan), n_p (dígito de n en la columna p), k y el límite disponible
    para el índice siguiente, calcula el rango contiguo de c' (decenas que se pasan) que
    produce un s_p realizable: 0 ≤ s_p ≤ 9k, donde s_p = 10·c' + (n_p − c).

    Retorna:
        (c_sig_min, c_sig_max) tras intersectar con [0, c_sig_lim].
        Si min > max, no hay opciones válidas para esta (p,c).
    """
    nine_k = 9 * k
    offset = n_p - c_llegan

    a = c_llegan - n_p
    if a >= 0:
        cmin = (a + 9) // 10
    else:
        cmin = - ((-a) // 10)

    b = nine_k - offset
    if b >= 0:
        cmax = b // 10
    else:
        cmax = b // 10

    if cmin < 0:
        cmin = 0
    if cmax > c_sig_lim:
        cmax = c_sig_lim

    return cmin, cmax


def ganancia_columna(s_p: int, peso_p: int) -> int:
    """
    Ganancia óptima en la columna p si la suma de dígitos de esa columna es s_p.

    Según el modelo: cada bloque de tres unidades en s_p permite poner dígitos 3/6/9
    que aportan una “unidad de creatividad” por el peso de la columna.

    Retorna:
        floor(s_p/3) * peso_p
    """
    return (s_p // 3) * peso_p


def construir_dp_columna(p: int,
                         k: int,
                         n_p: int,
                         peso_p: int,
                         dp_siguiente: List[int],
                         limite_siguiente: int,
                         limite_actual: int) -> List[int]:
    """
    Construye el vector dp(p, c) para c=0..limite_actual, usando dp(p+1, c') dado.

    Para cada c (decenas que llegan), iteramos c' válido (decenas que se pasan),
    calculamos s_p = 10·c' + (n_p − c), sumamos la ganancia local y el dp siguiente,
    y tomamos el mejor.

    Entradas:
        p (int): índice de columna actual (0=unidades, 1=decenas, ...).
        k (int): número de celdas.
        n_p (int): dígito de n en la columna p.
        peso_p (int): peso (creatividad por unidad) en la columna p.
        dp_siguiente (List[int]): arreglo con dp(p+1, c') para c' en [0, limite_siguiente].
        limite_siguiente (int): índice máximo válido para dp_siguiente.
        limite_actual (int): índice máximo de c que consideraremos en dp(p, c).

    Retorna:
        Lista cur_dp con tamaño limite_actual+1, donde cur_dp[c] = dp(p, c).
    """
    cur_dp = [NEG_INF] * (limite_actual + 1)
    nine_k = 9 * k

    for c in range(limite_actual + 1):
        cmin, cmax = rango_csig_valido(c, n_p, k, limite_siguiente)
        if cmin > cmax:
            continue

        best = NEG_INF
        s_p = 10 * cmin + (n_p - c)
        for c_sig in range(cmin, cmax + 1):
            if 0 <= s_p <= nine_k:
                nxt = dp_siguiente[c_sig]
                if nxt != NEG_INF:
                    gain = ganancia_columna(s_p, peso_p)
                    val = gain + nxt
                    if val > best:
                        best = val
            s_p += 10

        cur_dp[c] = best

    return cur_dp


def solve_one_case(k: int, n: int, P: List[int]) -> int:
    """
    Resuelve un caso del problema y retorna el máximo puntaje de creatividad.

    Modelo (texto de tu informe):
    - n = Σ_p n_p·10^p. En columna p: s_p = Σ_i d_(i,p), con 0 ≤ s_p ≤ 9k.
    - Debe cumplirse s_p + c = n_p + 10·c'. La ganancia óptima local es ⌊s_p/3⌋·p_p.
    - Definimos dp(p,c) y elegimos c' válido maximizando:
      ⌊(10·c' + (n_p − c))/3⌋·p_p + dp(p+1,c'), terminando con c=0.
    """
    n_digits = to_digits_base10(n)

    max_pos = max(len(n_digits), 5)

    cmax_global = cap_decenas_global(k)

    next_limit = 0
    next_dp = [0]

    for p in range(max_pos - 1, -1, -1):
        peso_p = P[p] if p < 5 else 0
        n_p = n_digits[p] if p < len(n_digits) else 0

        limite_actual = cap_decenas_por_columna(p, k, cmax_global)
        cur_dp = construir_dp_columna(
            p=p,
            k=k,
            n_p=n_p,
            peso_p=peso_p,
            dp_siguiente=next_dp,
            limite_siguiente=next_limit,
            limite_actual=limite_actual
        )

        next_dp = cur_dp
        next_limit = limite_actual

    ans = next_dp[0]
    if ans < 0:
        ans = 0
    return ans



def main() -> None:
    """
    Lee T casos desde stdin. Por cada caso, lee:
        k n p0 p1 p2 p3 p4
    e imprime una línea con el máximo puntaje (entero).

    Formato exacto de I/O, sin textos extra.
    """
    import sys
    data = sys.stdin.read().strip().split()
    if not data:
        return
    it = iter(map(int, data))
    T = next(it)
    out = []
    for _ in range(T):
        k = next(it); n = next(it)
        p0 = next(it); p1 = next(it); p2 = next(it); p3 = next(it); p4 = next(it)
        out.append(str(solve_one_case(k, n, [p0, p1, p2, p3, p4])))
    sys.stdout.write("\n".join(out))


if __name__ == "__main__":
    main()