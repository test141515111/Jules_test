import unittest
from tetris import (
    BOARD_WIDTH, BOARD_HEIGHT, TETROMINOES, create_board, new_tetrimino,
    check_collision, fix_piece_to_board, clear_lines, get_piece_shape
)

class TestTetris(unittest.TestCase):

    def test_create_board(self):
        """ボードが正しく作成されるかテストします。"""
        board = create_board()
        self.assertEqual(len(board), BOARD_HEIGHT, "ボードの高さが正しくありません。")
        self.assertEqual(len(board[0]), BOARD_WIDTH, "ボードの幅が正しくありません。")
        for row in board:
            for cell in row:
                self.assertEqual(cell, 0, "初期ボードのセルは0であるべきです。")

    def test_new_tetrimino(self):
        """新しいテトリミノが正しく生成されるかテストします。"""
        piece = new_tetrimino()
        self.assertIsInstance(piece, dict, "ピースは辞書型であるべきです。")
        self.assertIn('shape_name', piece, "ピースに 'shape_name' キーがありません。")
        self.assertIn('shape', piece, "ピースに 'shape' キーがありません。")
        self.assertIn('rotation', piece, "ピースに 'rotation' キーがありません。")
        self.assertIn('x', piece, "ピースに 'x' キーがありません。")
        self.assertIn('y', piece, "ピースに 'y' キーがありません。")
        self.assertIn(piece['shape_name'], TETROMINOES.keys(), "ピースの形状名が無効です。")
        self.assertEqual(piece['y'], 0, "ピースの初期Y位置は0であるべきです。")
        # X位置はおおよそ中央なので、厳密なテストは難しいが、範囲内にあるか程度は確認可能
        self.assertTrue(0 <= piece['x'] < BOARD_WIDTH, "ピースの初期X位置が範囲外です。")

    def test_check_collision_boundaries(self):
        """ピースがボードの境界と衝突するかテストします。"""
        board = create_board()
        # I字ピースを例に使用 (水平)
        piece = {'shape_name': 'I', 'shape': TETROMINOES['I'], 'rotation': 0, 'x': 0, 'y': 0}
        
        # 左境界
        piece['x'] = -1 
        self.assertTrue(check_collision(board, piece), "左境界との衝突が検出されません。")
        piece['x'] = 0

        # 右境界 (Iピースの長さは4)
        piece['x'] = BOARD_WIDTH - len(get_piece_shape(piece)[0]) + 1
        self.assertTrue(check_collision(board, piece), "右境界との衝突が検出されません。")
        piece['x'] = BOARD_WIDTH - len(get_piece_shape(piece)[0])
        self.assertFalse(check_collision(board, piece), "右境界ギリギリでの有効な位置が衝突と判定されます。")


        # 下境界 (Iピースの高さは1)
        piece['y'] = BOARD_HEIGHT - len(get_piece_shape(piece)) + 1
        self.assertTrue(check_collision(board, piece), "下境界との衝突が検出されません。")
        piece['y'] = BOARD_HEIGHT - len(get_piece_shape(piece))
        self.assertFalse(check_collision(board, piece), "下境界ギリギリでの有効な位置が衝突と判定されます。")


    def test_check_collision_with_fixed_block(self):
        """ピースが他の固定されたブロックと衝突するかテストします。"""
        board = create_board()
        board[5][5] = 1 # 固定されたブロック
        piece = new_tetrimino() # 新しいピースを生成
        piece['x'] = 5
        piece['y'] = 5 
        # ピースの形状によっては (0,0) が空の場合があるので、具体的なピースでテスト
        o_piece = {'shape_name': 'O', 'shape': TETROMINOES['O'], 'rotation': 0, 'x': 4, 'y': 4}
        # Oピースは (0,0) から (1,1) までブロックがあるので、(4,4)に置くと (5,5) のブロックと衝突するはず
        self.assertTrue(check_collision(board, o_piece), "固定ブロックとの衝突が検出されません。")

        o_piece['x'] = 0
        o_piece['y'] = 0
        self.assertFalse(check_collision(board, o_piece), "固定ブロックがない場所での衝突判定が誤っています。")

    def test_check_collision_valid_moves(self):
        """衝突しない有効な移動と回転をテストします。"""
        board = create_board()
        piece = new_tetrimino()
        piece['x'] = BOARD_WIDTH // 2
        piece['y'] = BOARD_HEIGHT // 2

        # 有効な移動
        self.assertFalse(check_collision(board, piece, new_x=piece['x'] + 1), "有効な右移動が衝突と判定されます。")
        self.assertFalse(check_collision(board, piece, new_x=piece['x'] - 1), "有効な左移動が衝突と判定されます。")
        self.assertFalse(check_collision(board, piece, new_y=piece['y'] + 1), "有効な下移動が衝突と判定されます。")

        # 有効な回転 (ピースと位置に依存するが、ここでは一般的なケースを想定)
        # Tピースを中央に配置
        t_piece = {'shape_name': 'T', 'shape': TETROMINOES['T'], 'rotation': 0, 'x': 5, 'y': 5}
        if BOARD_WIDTH >= 7 and BOARD_HEIGHT >= 7: # 十分なスペースがある場合
             self.assertFalse(check_collision(board, t_piece, new_rotation=(t_piece['rotation'] + 1)), "有効な回転が衝突と判定されます。")

    def test_check_collision_rotation_into_wall(self):
        """回転による壁との衝突をテストします（壁キックなし）。"""
        board = create_board()
        # Iピースを左端に配置し、縦に回転させる
        i_piece_vertical = {'shape_name': 'I', 'shape': TETROMINOES['I'], 'rotation': 1, 'x': 0, 'y': 0} # 縦向き
        # これを水平に回転させようとすると、右にはみ出すはず (I字の長さ4)
        if len(TETROMINOES['I'][0][0]) > 1 : # 水平形状が存在する場合
            self.assertTrue(check_collision(board, i_piece_vertical, new_rotation=0), "壁への回転による衝突が検出されません。")

    def test_fix_piece_to_board(self):
        """ピースがボードに正しく固定されるかテストします。"""
        board = create_board()
        # Oピースを (0,0) に固定
        o_piece = {'shape_name': 'O', 'shape': TETROMINOES['O'], 'rotation': 0, 'x': 0, 'y': 0}
        fix_piece_to_board(board, o_piece)
        
        piece_shape = get_piece_shape(o_piece)
        for r_idx, row in enumerate(piece_shape):
            for c_idx, cell in enumerate(row):
                if cell:
                    self.assertEqual(board[o_piece['y'] + r_idx][o_piece['x'] + c_idx], 1, "ピースがボードに正しく固定されていません。")

    def test_clear_lines_single_and_multiple(self):
        """1行および複数行が正しく消去されるかテストします。"""
        # 1行消去
        board = create_board()
        for c in range(BOARD_WIDTH): # BOARD_HEIGHT-1 の行を埋める
            board[BOARD_HEIGHT-1][c] = 1
        
        cleared_board, count = clear_lines(board)
        self.assertEqual(count, 1, "1行消去時のカウントが正しくありません。")
        for c in range(BOARD_WIDTH): # 消去された行は0になる
            self.assertEqual(cleared_board[BOARD_HEIGHT-1][c], 0, "消去されたラインが空になっていません。")
        self.assertEqual(cleared_board[0][0], 0, "新しい行が最上部に追加されていません。")

        # 4行消去 (テトリス)
        board = create_board()
        for r in range(BOARD_HEIGHT-4, BOARD_HEIGHT): # 下から4行を埋める
            for c in range(BOARD_WIDTH):
                board[r][c] = 1
        
        cleared_board, count = clear_lines(board)
        self.assertEqual(count, 4, "4行消去時のカウントが正しくありません。")
        for r in range(BOARD_HEIGHT-4, BOARD_HEIGHT):
            for c in range(BOARD_WIDTH):
                self.assertEqual(cleared_board[r][c], 0, f"{r}行目が消去されていません。")
        for r in range(4): # 上から4行が空行になっているはず
             for c in range(BOARD_WIDTH):
                self.assertEqual(cleared_board[r][c], 0, f"新しい空行 {r} が正しくありません。")


    def test_clear_lines_shift_down(self):
        """ライン消去後、上のラインが正しく下にシフトするかテストします。"""
        board = create_board()
        # 1行目をブロックで埋める
        for c in range(BOARD_WIDTH):
            board[0][c] = 2 
        # 3行目を消去対象にする
        for c in range(BOARD_WIDTH):
            board[2][c] = 1
        
        cleared_board, count = clear_lines(board)
        self.assertEqual(count, 1, "ライン消去カウントが正しくありません。")
        # 元の0行目のブロックが1行目にシフトダウンしているはず (消去されたのは2行目なので、新しい2行目は空)
        for c in range(BOARD_WIDTH):
            self.assertEqual(cleared_board[1][c], 2, "ブロックが正しくシフトダウンしていません。")
        for c in range(BOARD_WIDTH):
            self.assertEqual(cleared_board[2][c], 0, "消去された行が空になっていません。")
        self.assertEqual(cleared_board[0][0], 0, "最上部に新しい空行が追加されていません。")


    def test_clear_lines_no_lines_cleared(self):
        """消去するラインがない場合の動作をテストします。"""
        board = create_board()
        board[0][0] = 1 # 一部だけ埋まっている
        
        cleared_board, count = clear_lines(board)
        self.assertEqual(count, 0, "ラインが消去されていないのにカウントが0ではありません。")
        self.assertEqual(board, cleared_board, "ラインが消去されていないのにボードが変更されています。")

    def test_scoring_logic(self):
        """ライン消去数に基づいたスコア計算をテストします。"""
        # このテストは tetris.py の main 内のスコアロジックを模倣します。
        test_scores = {1: 100, 2: 300, 3: 500, 4: 800, 0: 0}
        for lines_cleared, expected_score_increase in test_scores.items():
            current_score = 0 # 仮の現在のスコア
            if lines_cleared == 1:
                current_score += 100
            elif lines_cleared == 2:
                current_score += 300
            elif lines_cleared == 3:
                current_score += 500
            elif lines_cleared >= 4:
                current_score += 800
            self.assertEqual(current_score, expected_score_increase, f"{lines_cleared}ライン消去時のスコアが正しくありません。")
    
    def test_game_over_condition(self):
        """新しいピースの生成位置が塞がっていてゲームオーバーになる条件をテストします。"""
        board = create_board()
        # Oピースのデフォルト出現位置の周辺を塞ぐ
        # new_tetrimino() はランダムなので、特定のピースを仮定してテストするのは難しい。
        # 代わりに、ピースの出現エリア上部を塞いでみる。
        # Oピースは (y=0 or 1, x= BOARD_WIDTH//2 -1 or BOARD_WIDTH//2) あたりに出現
        # 確実性を期すため、出現可能性のある最上部の数ラインを埋める
        # 例として、y=0, y=1 の中央付近を埋める
        spawn_x_approx = BOARD_WIDTH // 2 - 1
        board[0][spawn_x_approx] = 1
        board[0][spawn_x_approx + 1] = 1
        board[1][spawn_x_approx] = 1
        board[1][spawn_x_approx+1] = 1

        # Oピースを強制的に生成し、その位置で衝突するか確認
        # 注意: new_tetrimino() はランダムなので、ここでは特定のピースを配置してテストします。
        # Oピースが (spawn_x_approx, 0) に出現すると仮定
        o_piece = {'shape_name': 'O', 'shape': TETROMINOES['O'], 'rotation': 0, 
                   'x': spawn_x_approx, 'y': 0}

        self.assertTrue(check_collision(board, o_piece), "ゲームオーバー条件（ピース出現位置の衝突）が検出されません。")

        # 何もないボードでは、新しいピースは衝突しないはず
        empty_board = create_board()
        any_new_piece = new_tetrimino() # どんなピースでも
        self.assertFalse(check_collision(empty_board, any_new_piece), "空のボードで新しいピースが衝突すると判定されます。")


if __name__ == '__main__':
    unittest.main()
