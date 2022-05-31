var n = 4;
function printBoard(board) {
    for (var i = 0; i < 4; i++) {
        for (var j = 0; j < 4; j++)
            if (board[i][j] == 1) {
                console.log("Q\t");
                document.getElementById("numberP").innerHTML += ("Q &nbsp;&nbsp;");
            }
            else {
                console.log("_\t");
                document.getElementById("numberP").innerHTML += ("_ &nbsp;&nbsp;");
            }
            }
        console.log("\n");
        document.getElementById("numberP").innerHTML += ("<br>");
    }
}
function toPlaceOrNotToPlace(board, row, col) {
    for (var i = 0; i < col; i++) {
        if (board[row][i] == 1)
            return false;
    }
    for (var i = row, j = col; i >= 0 && j >= 0; i--, j--) {
        if (board[i][j] == 1)
            return false;
    }
    for (var i = row, j = col; j >= 0 && i < 4; i++, j--) {
        if (board[i][j] == 1)
            return false;
    }
    return true;
}
function theBoardSolver(board, col) {
    if (col >= 4)
        return true;
    for (var i = 0; i < 4; i++) {
        if (toPlaceOrNotToPlace(board, i, col)) {
            board[i][col] = 1;
            if (theBoardSolver(board, col + 1))
                return true;
            board[i][col] = 0;
        }
    }
    return false;
}
var board = new Array();
board.push([0, 0, 0, 0]);
board.push([0, 0, 0, 0]);
board.push([0, 0, 0, 0]);
board.push([0, 0, 0, 0]);
if (!theBoardSolver(board, 0)) {
    console.log("solution not found");
}
printBoard(board);
/*
public static void main(String[] args) {
    scan = new Scanner(System.in);
    System.out.println("State the value of N in this program!");
    N = scan.nextInt();
    int[][] board = new int[N][N];
    if (!theBoardSolver(board, 0)) {
        System.out.println("Solution not found.");
    }
    printBoard(board);
}
*/
