import java.io.*;
import java.util.*;

/**
Diseno y Analisis de Algoritmos 2025-20
Problema 1

- @author Santiago Rodriguez Mora - 202110332
- @author Valeria Torres Gomez - 202110363
 */


public class ProyectoDalgoP1 {

    private static final long PUNTAJE_MINIMO = Long.MIN_VALUE / 4;

    public static void main(String[] args) throws Exception {
        FastReader lector = new FastReader(System.in);
        StringBuilder salida = new StringBuilder();

        long inicio = System.nanoTime();

        int casos;
        try {
            casos = lector.nextInt();
        } catch (Exception e) {
            return;
        }

        for (int caso = 0; caso < casos; caso++) {
            int k = lector.nextInt();
            int n = lector.nextInt();
            int[] pesos = new int[5];
            for (int i = 0; i < 5; i++) {
                pesos[i] = lector.nextInt();
            }

            long mejorPuntaje = resolverCaso(k, n, pesos);
            salida.append(mejorPuntaje).append('\n');
        }

        System.out.print(salida.toString());

        long fin = System.nanoTime();
        long transcurridoMs = (fin - inicio) / 1_000_000;
        long minutos = transcurridoMs / 60_000;
        long segundos = (transcurridoMs % 60_000) / 1_000;
        long milis = transcurridoMs % 1_000;
        System.err.printf("[Tiempo total] %02d:%02d.%03d (mm:ss.mmm)%n", minutos, segundos, milis);
    }


    private static long solveKEquals1(int n, int[] pesos) {
        long ans = 0;
        int p = 0;
        int x = n;
        while (p < 5 || x > 0) {
            int d = x % 10;
            int peso = (p < 5 ? pesos[p] : 0);
            if (d == 3) ans += peso;
            else if (d == 6) ans += 2L * peso;
            else if (d == 9) ans += 3L * peso;
            x /= 10;
            p++;
        }
        return ans;
    }


    private static long resolverCaso(int k, int n, int[] pesos) {

        if (k == 1) {
        return solveKEquals1(n, pesos);
        }

        int[] digitos = digitosDecimales(n);
        int ultimaColumna = Math.max(digitos.length, 5);
        int nuevePorK = 9 * k;
        int limiteGlobal = limiteAcarreosGlobal(nuevePorK);

        long[] dpSiguiente = new long[]{0L};
        int limiteSiguiente = 0;

        for (int columna = ultimaColumna - 1; columna >= 0; columna--) {
            int pesoColumna = columna < 5 ? pesos[columna] : 0;
            int digitoObjetivo = columna < digitos.length ? digitos[columna] : 0;

            int limiteActual = limiteAcarreosColumna(columna, nuevePorK, limiteGlobal);
            long[] dpActual = construirDpColumna(
                    nuevePorK,
                    digitoObjetivo,
                    pesoColumna,
                    dpSiguiente,
                    limiteSiguiente,
                    limiteActual
            );
            dpSiguiente = dpActual;
            limiteSiguiente = limiteActual;
        }

        long respuesta = dpSiguiente[0];
        return Math.max(respuesta, 0);
    }


    private static long[] construirDpColumna(
            int nuevePorK,
            int digitoObjetivo,
            int pesoColumna,
            long[] dpSiguiente,
            int limiteSiguiente,
            int limiteActual
    ) {
        long[] dp = new long[limiteActual + 1];
        Arrays.fill(dp, PUNTAJE_MINIMO);
        int maximoSuma = nuevePorK;
        long triplePeso = 3L * pesoColumna;

        long[][] puntajePorResiduo = new long[3][limiteSiguiente + 1];
        for (int acarreoSaliente = 0; acarreoSaliente <= limiteSiguiente; acarreoSaliente++) {
            long valorSiguiente = dpSiguiente[acarreoSaliente];
            if (valorSiguiente == PUNTAJE_MINIMO) {
                puntajePorResiduo[0][acarreoSaliente] = PUNTAJE_MINIMO;
                puntajePorResiduo[1][acarreoSaliente] = PUNTAJE_MINIMO;
                puntajePorResiduo[2][acarreoSaliente] = PUNTAJE_MINIMO;
                continue;
            }

            long base = valorSiguiente + triplePeso * acarreoSaliente;
            for (int residuo = 0; residuo < 3; residuo++) {
                long extra = (long) pesoColumna * Math.floorDiv(acarreoSaliente + digitoObjetivo - residuo, 3);
                puntajePorResiduo[residuo][acarreoSaliente] = base + extra;
            }
        }

        for (int residuo = 0; residuo < 3; residuo++) {
            Deque<Integer> deque = new ArrayDeque<>();
            int limiteProcesado = -1;
            long[] puntajes = puntajePorResiduo[residuo];

            for (int acarreoEntrante = residuo; acarreoEntrante <= limiteActual; acarreoEntrante += 3) {
                int minimo = ceilDiv(acarreoEntrante - digitoObjetivo, 10);
                if (minimo < 0) {
                    minimo = 0;
                }
                int maximo = Math.floorDiv(maximoSuma + acarreoEntrante - digitoObjetivo, 10);
                if (maximo > limiteSiguiente) {
                    maximo = limiteSiguiente;
                }
                if (maximo < minimo) {
                    dp[acarreoEntrante] = PUNTAJE_MINIMO;
                    continue;
                }

                while (limiteProcesado < maximo) {
                    limiteProcesado++;
                    long valor = puntajes[limiteProcesado];
                    while (!deque.isEmpty() && puntajes[deque.peekLast()] <= valor) {
                        deque.pollLast();
                    }
                    deque.addLast(limiteProcesado);
                }

                while (!deque.isEmpty() && deque.peekFirst() < minimo) {
                    deque.pollFirst();
                }

                if (deque.isEmpty()) {
                    dp[acarreoEntrante] = PUNTAJE_MINIMO;
                    continue;
                }

                long mejor = puntajes[deque.peekFirst()];
                if (mejor == PUNTAJE_MINIMO) {
                    dp[acarreoEntrante] = PUNTAJE_MINIMO;
                } else {
                    long resta = (long) pesoColumna * ((acarreoEntrante - residuo) / 3);
                    dp[acarreoEntrante] = mejor - resta;
                }
            }
        }
        return dp;
    }


    private static int limiteAcarreosColumna(int columna, int nuevePorK, int limiteGlobal) {
        int estimado = (columna * nuevePorK) / 10 + 2;
        return Math.min(limiteGlobal, estimado);
    }


    private static int limiteAcarreosGlobal(int nuevePorK) {
        return nuevePorK / 10 + 2;
    }


    private static int ceilDiv(int valor, int divisor) {
        return -Math.floorDiv(-valor, divisor);
    }


    private static int[] digitosDecimales(int numero) {
        if (numero == 0) {
            return new int[]{0};
        }

        int[] buffer = new int[12];
        int tam = 0;
        int actual = numero;
        while (actual > 0) {
            buffer[tam++] = actual % 10;
            actual /= 10;
        }
        return Arrays.copyOf(buffer, tam);
    }


    private static class FastReader {
        private final InputStream input;
        private final byte[] buffer = new byte[1 << 16];
        private int indice = 0;
        private int longitud = 0;

        FastReader(InputStream input) {
            this.input = input;
        }

        private int read() throws IOException {
            if (indice >= longitud) {
                longitud = input.read(buffer);
                indice = 0;
                if (longitud <= 0) {
                    return -1;
                }
            }
            return buffer[indice++];
        }

        int nextInt() throws IOException {
            int c;
            int signo = 1;
            int valor = 0;
            do {
                c = read();
            } while (c <= ' ');
            if (c == '-') {
                signo = -1;
                c = read();
            }
            while (c > ' ') {
                valor = valor * 10 + (c - '0');
                c = read();
            }
            return valor * signo;
        }
    }
}