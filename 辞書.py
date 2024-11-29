import flet as ft

def main(page: ft.Page):
    # ページの基本設定
    page.title = "ナビゲーションとリストの例"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 10

    # メインコンテンツエリア
    content_area = ft.Container(
        width=600,
        height=400,
        bgcolor=ft.colors.WHITE,
        border_radius=10,
        padding=20,
        content=ft.Text("コンテンツをここに表示", size=16)
    )

    # ナビゲーションの宛先が変更されたときの処理
    def change_nav_destination(e):
        selected_index = e.control.selected_index
        nav_destinations = ["ホーム", "プロフィール", "設定", "お知らせ"]
        content_area.content = ft.Text(f"選択された画面: {nav_destinations[selected_index]}", size=16)
        content_area.update()

    # ナビゲーションレール（縦型ナビゲーションバー）
    navigation_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        max_width=200,
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.icons.HOME_OUTLINED,
                selected_icon=ft.icons.HOME,
                label="ホーム"
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.PERSON_OUTLINE,
                selected_icon=ft.icons.PERSON,
                label="プロフィール"
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.SETTINGS_OUTLINED,
                selected_icon=ft.icons.SETTINGS,
                label="設定"
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.NOTIFICATIONS_OUTLINED,
                selected_icon=ft.icons.NOTIFICATIONS,
                label="お知らせ"
            )
        ],
        on_change=change_nav_destination
    )

    # 展開可能なタイル（ユーザー情報）
    expansion_tile = ft.ExpansionTile(
        title=ft.Text("ユーザー情報"),
        subtitle=ft.Text("詳細を表示"),
        trailing=ft.Icon(ft.icons.KEYBOARD_ARROW_DOWN),
        controls=[
            ft.ListTile(
                title=ft.Text("名前"),
                trailing=ft.Text("山田 太郎")
            ),
            ft.ListTile(
                title=ft.Text("メールアドレス"),
                trailing=ft.Text("yamada@example.com")
            ),
            ft.ListTile(
                title=ft.Text("電話番号"),
                trailing=ft.Text("090-1234-5678")
            )
        ]
    )

    # リストタイルのコンテナ
    list_tile_container = ft.Column(
        spacing=10,
        controls=[
            ft.ListTile(
                title=ft.Text("アカウント設定"),
                leading=ft.Icon(ft.icons.ACCOUNT_CIRCLE),
                trailing=ft.Icon(ft.icons.ARROW_FORWARD_IOS)
            ),
            ft.ListTile(
                title=ft.Text("プライバシー設定"),
                leading=ft.Icon(ft.icons.PRIVACY_TIP),
                trailing=ft.Icon(ft.icons.ARROW_FORWARD_IOS)
            ),
            ft.ListTile(
                title=ft.Text("ヘルプセンター"),
                leading=ft.Icon(ft.icons.HELP),
                trailing=ft.Icon(ft.icons.ARROW_FORWARD_IOS)
            )
        ]
    )

    # メインレイアウト
    main_layout = ft.Row(
        controls=[
            navigation_rail,
            ft.VerticalDivider(width=1),
            ft.Column(
                width=400,
                controls=[
                    expansion_tile,
                    list_tile_container
                ]
            ),
            content_area
        ],
        spacing=10,
        vertical_alignment=ft.CrossAxisAlignment.START
    )

    # ページにレイアウトを追加
    page.add(main_layout)
    page.update()

# アプリケーションの実行
ft.app(target=main)