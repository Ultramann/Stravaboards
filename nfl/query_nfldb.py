import psycopg2 
import pandas as pd

class Connection(object):
    def __init__(self):
        self.conn = psycopg2.connect(dbname='nfldb')

    def close(self):
        self.conn.close()

    def get_yr_wk(self, year, week):
        defense_stats = '''
                    yds_against, tds_against, d_ast, d_ffum, d_frec, d_frec_yds,
                    d_frec_tds, d_int, d_int_yds, d_int_tds, d_qbhit, d_sk,
                    d_sk_yds, d_tkl, d_tkl_loss, d_tkl_loss_yds, d_tkl_primary
        '''
        agg_stats = '''
                      p.player_id AS p_id
                    , SUM(receiving_yds) re_yds
                    , SUM(receiving_yac_yds) re_yac
                    , SUM(receiving_tar) re_targets
                    , SUM(receiving_rec) receptions
                    , SUM(receiving_tds) re_tds
                    , SUM(rushing_yds) ru_yds
                    , SUM(rushing_att) ru_att
                    , SUM(rushing_loss) ru_loss
                    , SUM(rushing_loss_yds) ru_loss_yds
                    , SUM(rushing_tds) ru_tds
                    , SUM(passing_cmp_air_yds) p_comp_air_yds
                    , SUM(passing_incmp) p_incmp
                    , SUM(passing_incmp_air_yds) p_incmp_air_yds
                    , SUM(passing_int) p_interceptions
                    , SUM(passing_sk) p_sacks
                    , SUM(passing_att) p_atts
                    , SUM(passing_cmp) p_comps
                    , SUM(passing_yds) p_yds
                    , SUM(passing_tds) p_tds
                    , SUM(receiving_tds) + SUM(rushing_tds) + SUM(passing_tds) AS total_tds
                    , SUM(receiving_yds) + SUM(rushing_yds) + SUM(passing_yds) AS total_yds
                    , SUM(receiving_yds) + SUM(rushing_yds) AS yds_against
                    , SUM(receiving_tds) + SUM(rushing_tds) AS tds_against
                    , SUM(defense_ast) d_ast
                    , SUM(defense_ffum) d_ffum
                    , SUM(defense_frec) d_frec
                    , SUM(defense_frec_yds) d_frec_yds
                    , SUM(defense_frec_tds) d_frec_tds
                    , SUM(defense_int) d_int
                    , SUM(defense_int_yds) d_int_yds
                    , SUM(defense_int_tds) d_int_tds
                    , SUM(defense_qbhit) d_qbhit
                    , SUM(defense_sk) d_sk
                    , SUM(defense_sk_yds) d_sk_yds
                    , SUM(defense_tkl) d_tkl
                    , SUM(defense_tkl_loss) d_tkl_loss
                    , SUM(defense_tkl_loss_yds) d_tkl_loss_yds
                    , SUM(defense_tkl_primary) d_tkl_primary
        '''
        query = '''
            WITH weeks_games AS (
                    SELECT gsis_id, home_team, away_team
                    FROM game
                    WHERE season_year = {year}
                        AND season_type = 'Regular'
                        AND week = {week}
                ), 
                off_player_stats AS (
                    SELECT {agg_stats}
                    FROM weeks_games wg
                    JOIN play_player pp
                        ON pp.gsis_id = wg.gsis_id 
                    JOIN player p
                        ON p.player_id = pp.player_id
                    WHERE (position = 'WR' OR position = 'RB' OR position = 'TE' OR position = 'QB')
                    GROUP BY p_id
                ),
                offense AS (
                    SELECT DISTINCT p.full_name AS name, CAST(p.position AS VARCHAR) AS pos, 
                                    pp.team AS team,
                                    total_tds, total_yds,
                                    re_yds, re_yac, re_targets, receptions, re_tds, 
                                    ru_yds, ru_att, ru_loss, ru_loss_yds, ru_tds, 
                                    p_comp_air_yds, p_incmp_air_yds, p_sacks, p_atts, p_comps, 
                                    p_incmp, p_interceptions, p_yds, p_tds,
                                    {defense_stats},
                                    CASE WHEN pp.team = wg.home_team THEN wg.away_team
                                    ELSE wg.home_team END AS opp
                    FROM weeks_games wg 
                    JOIN play_player pp
                        ON pp.gsis_id = wg.gsis_id
                    JOIN player p
                        ON p.player_id = pp.player_id
                    JOIN off_player_stats ops
                        ON ops.p_id = p.player_id
                ),
                def_player_stats AS (
                    SELECT {agg_stats}
                    FROM weeks_games wg
                    JOIN play_player pp
                        ON pp.gsis_id = wg.gsis_id 
                    JOIN player p
                        ON p.player_id = pp.player_id
                    WHERE (position <> 'WR' AND position <> 'RB' 
                       AND position <> 'TE' AND position <> 'QB')
                    GROUP BY p_id
                ),
                defense_stats AS (
                    SELECT  pp.team as name
                    ,       SUM(re_yds) re_yds
                    ,       SUM(re_yac) re_yac 
                    ,       SUM(re_targets) re_targets
                    ,       SUM(receptions) receptions
                    ,       SUM(re_tds) re_tds
                    ,       SUM(ru_yds) ru_yds
                    ,       SUM(ru_att) ru_att
                    ,       SUM(ru_loss) ru_loss
                    ,       SUM(ru_loss_yds) ru_loss_yds
                    ,       SUM(ru_tds) ru_tds
                    ,       SUM(p_comp_air_yds) p_comp_air_yds
                    ,       SUM(p_incmp) p_incmp
                    ,       SUM(p_incmp_air_yds) p_incmp_air_yds
                    ,       SUM(p_interceptions) p_interceptions
                    ,       SUM(p_sacks) p_sacks
                    ,       SUM(p_atts) p_atts
                    ,       SUM(p_comps) p_comps
                    ,       SUM(p_yds) p_yds
                    ,       SUM(p_tds) p_tds
                    ,       SUM(total_tds) AS total_tds
                    ,       SUM(total_yds) AS total_yds
                    ,       SUM(yds_against) yds_against
                    ,       SUM(tds_against) tds_against
                    ,       SUM(d_ast) d_ast
                    ,       SUM(d_ffum) d_ffum
                    ,       SUM(d_frec) d_frec
                    ,       SUM(d_frec_yds) d_frec_yds
                    ,       SUM(d_frec_tds) d_frec_tds
                    ,       SUM(d_int) d_int
                    ,       SUM(d_int_yds) d_int_yds
                    ,       SUM(d_int_tds) d_int_tds
                    ,       SUM(d_qbhit) d_qbhit
                    ,       SUM(d_sk) d_sk
                    ,       SUM(d_sk_yds) d_sk_yds
                    ,       SUM(d_tkl) d_tkl
                    ,       SUM(d_tkl_loss) d_tkl_loss
                    ,       SUM(d_tkl_loss_yds) d_tkl_loss_yds
                    ,       SUM(d_tkl_primary) d_tkl_primary
                    FROM weeks_games wg
                    JOIN play_player pp
                        ON pp.gsis_id = wg.gsis_id
                    JOIN def_player_stats dps
                        ON dps.p_id = pp.player_id
                    GROUP BY name
                ),
                defense AS (
                    SELECT DISTINCT name, 'D' AS pos, name AS team,
                                    0 total_tds, 0 total_yds,
                                    0 re_yds, 0 re_yac, 0 re_targets, 0 receptions, 0 re_tds, 
                                    0 ru_yds, 0 ru_att, 0 ru_loss, 0 ru_loss_yds, 0 ru_tds, 
                                    0 p_comp_air_yds, 0 p_incmp_air_yds, 0 p_sacks, 0 p_atts, 
                                    0 p_comps, 0 p_incmp, 0 p_interceptions, 0 p_yds, 0 p_tds,
                                    {defense_stats},
                                    CASE WHEN name = wg.home_team THEN wg.away_team
                                    ELSE wg.home_team END AS opp
                    FROM weeks_games wg 
                    JOIN play_player pp
                        ON pp.gsis_id = wg.gsis_id
                    JOIN player p
                        ON p.player_id = pp.player_id
                    JOIN defense_stats ds
                        ON ds.name = pp.team
                )
                SELECT * FROM defense
                UNION
                SELECT * FROM offense
        '''.format(year=year, week=week, agg_stats=agg_stats, defense_stats=defense_stats)

        return pd.read_sql(query, self.conn)
