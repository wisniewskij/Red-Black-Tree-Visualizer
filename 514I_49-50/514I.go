package taocp3

import "math"

// Algorithm 5.1.4.I
func InsertIntoTableau(P [][]int, x int) [][]int {
	j := math.MaxInt
	for i := range P { // I1
		j = min(j, len(P[i]))
		for j > 0 && P[i][j-1] > x { // I2
			j--
		}
		if j != len(P[i]) { // I3
			x, P[i][j] = P[i][j], x
		} else { // I4
			P[i] = append(P[i], x)
			return P
		}
	}

	P = append(P, []int{x})
	return P
}
