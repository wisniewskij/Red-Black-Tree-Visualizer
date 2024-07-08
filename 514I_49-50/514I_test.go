package taocp3

import (
	"reflect"
	"testing"
)

func TestInsertIntoTableau(t *testing.T) {
	P := [][]int{
		{1, 3, 5, 9, 12, 16},
		{2, 6, 10, 15},
		{4, 13, 14},
		{11},
		{17},
	}
	x := 8
	want := [][]int{
		{1, 3, 5, 8, 12, 16},
		{2, 6, 9, 15},
		{4, 10, 14},
		{11, 13},
		{17},
	}
	if got := InsertIntoTableau(P, x); !reflect.DeepEqual(got, want) {
		t.Fatalf("InsertIntoTableau(%#v, %#v) == %#v; want %#v",
			P, x, got, want)
	}
}

func TestInsertIntoTableauMinimumValue(t *testing.T) {
	P := [][]int{
		{2, 4, 6, 10, 13, 17},
		{3, 7, 11, 16},
		{5, 14, 15},
		{12},
		{18},
	}
	x := 1
	want := [][]int{
		{1, 4, 6, 10, 13, 17},
		{2, 7, 11, 16},
		{3, 14, 15},
		{5},
		{12},
		{18},
	}
	if got := InsertIntoTableau(P, x); !reflect.DeepEqual(got, want) {
		t.Fatalf("InsertIntoTableau(%#v, %#v) == %#v; want %#v",
			P, x, got, want)
	}
}

func TestInsertIntoTableauEmptyTableau(t *testing.T) {
	P := [][]int{}
	x := 1
	want := [][]int{
		{1},
	}
	if got := InsertIntoTableau(P, x); !reflect.DeepEqual(got, want) {
		t.Fatalf("InsertIntoTableau(%#v, %#v) == %#v; want %#v",
			P, x, got, want)
	}
}
