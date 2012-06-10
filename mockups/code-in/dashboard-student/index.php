<?php include '../includes/header.php'?>

    <div class="grid_3 side">
        <div class="block block-main-nav">
            <ul class="menu">
                <li class="active"><a href="javascript:void(0)">My Dashboard</a></li>
                <li><a href="javascript:void(0)">About Us</a></li>
                <li><a href="javascript:void(0)">Get Started</a></li>
                <li><a href="javascript:void(0)">Participating Organizations</a></li>
                <li><a href="javascript:void(0)">Blog</a></li>
            </ul>
        </div>
        <!-- end .block.block-main-nav -->
        
        <div class="block block-status block-status-sm">
            <div class="block-status-user">
                You are logged in as: <a href="javascript:void(0)">eric_schmidt@gmail.com</a> <a href="javascript:void(0)">(change)</a>
            </div>
            <div class="block-status-action block-status-action-single clearfix">
                <a href="javascript:void(0)" class="block-status-action-dashboard"><span>My Dashboard</span></a>
            </div>
        </div>
        <!-- end .block.block-status.block-status-sm -->
    </div>
    <!-- end .grid_3.side -->
    <div class="grid_9 main">
        <div class="block block-user-welcome clearfix">
            <div class="block-user-welcome-title">
                <span class="subhead">Student name</span>
                <span class="name">Eric Schmidt</span>
            </div>
            <div class="user-ranking">
                <div class="user-ranking-item">
                    <span class="cap">Score</span>
                    <span class="number">285</span>
                    <span class="count">points</span>
                </div>
                <div class="user-ranking-item">
                    <span class="cap">Rank</span>
                    <span class="number">#62</span>
                    <span class="count">Top 5%</span>
                </div>
            </div>
            <form action="#" method="post">
            <input type="submit" class="btn" value="Search for tasks" />
            </form>
        </div>
        <!-- end .block.block-user-welcome -->
        <div class="block block-task block-featured-task block-student-featured-task level-difficult">
            <div class="cog"></div>
            <div class="block-title">
                Write documentation for export function
                <span class="project">Drupal Foundation</span>
            </div>
            <div class="block-task-difficulty">
                <span class="difficulty">Difficulty: <span class="emph">Medium</span></span>
                <span class="status">Status: <span class="emph">In progress</span></span>
                <span class="remaining">Time left: <span class="emph">5 hrs 6 min</span></span>
                <span class="mentor">Mentor: <span class="emph">Carol Smith</span></span>
            </div>
            <div class="block-content clearfix">
                <div class="block-task-countdown">
                    <div class="stopwatch percent-33 clearfix">
                        <div class="stopwatch-watch"></div>
                        <div class="stopwatch-remaining clearfix">
                            <div class="stopwatch-time">
                                <div class="stopwatch-time-c">
                                    <div class="time time-first">
                                        <span class="number">35</span><span class="cap">days</span>
                                    </div>
                                    <div class="time">
                                        <span class="number">17</span><span class="cap">hours</span>
                                    </div>
                                </div>
                            </div>
                            <span class="remain">Remaining</span>
                            <span class="timestamp">as of 7/23 @3:30GMT</span>
                        </div>
                    </div>
                    <!-- end .stockwatch -->
                </div>
                <!-- end .block-task-countdown -->
                <div class="block-task-description">
                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis porttitor purus massa. Aliquam erat volutpat. Maecenas vitae neque ipsum. Morbi scelerisque varius augue ac euismod. Pellentesque euismod augue a justo mollis eu tempor nunc ultricies. Fusce pharetra convallis dignissim...</p>
                </div>
                <!-- end .block-task-description -->
            </div>
            <div class="block-footer">
                <a href="javascript:void(0)">View task</a> <a href="javascript:void(0)">Submit code</a>
            </div>
        </div>
        <!-- end .block.block-featured-task -->
        <div class="block block-completed-tasks">
            <div class="block-title">My Completed Tasks</div>
            <div class="block-filter clearfix">
            	<div class="block-filter-option block-filter-option-difficulty">
            		<select class="uniform">
            			<option>Difficulty: All</option>
            			<option>Difficulty: Easy</option>
            			<option>Difficulty: Medium</option>
            			<option>Difficulty: Difficult</option>
            		</select>
            	</div>
            </div>
            <div class="block-filter-sort">
            	Sort by: <a href="javascript:void(0)" class="block-filter-sort-link block-filter-sort-deadline">Deadline</a>
            </div>
            <div class="task-single task-single-in-progress level-difficult clearfix">
                <div class="cog"></div>
                <div class="task-single-content clearfix">
                    <span class="task-single-title"><a href="javascript:void(0)">Update Image Import Module</a></span>
                    <div class="task-single-content-bottom clearfix">
                        <div class="task-single-content-col1">
                            <span class="task-single-info task-single-project"><a href="javascript:void(0)">Mozilla Project</a></span>
                        </div>
                        <div class="task-single-content-col2">
                            <span class="task-single-info task-single-completed-date">Completed: July 23 2011 2:21GMT</span>
                        </div>
                    </div>
                </div>
            </div>
            <!-- end .task-single -->
            <div class="task-single task-single-in-progress even level-medium clearfix">
                <div class="cog"></div>
                <div class="task-single-content clearfix">
                    <span class="task-single-title"><a href="javascript:void(0)">Translate Plug-in Documentation from English to Arabic</a></span>
                    <div class="task-single-content-bottom clearfix">
                        <div class="task-single-content-col1">
                            <span class="task-single-info task-single-project"><a href="javascript:void(0)">Mozilla Project</a></span>
                        </div>
                        <div class="task-single-content-col2">
                            <span class="task-single-info task-single-completed-date">Completed: July 21 2011 14:33GMT</span>
                        </div>
                    </div>
                </div>
            </div>
            <!-- end .task-single -->
            <div class="task-single task-single-in-progress level-easy clearfix">
                <div class="cog"></div>
                <div class="task-single-content clearfix">
                    <span class="task-single-title"><a href="javascript:void(0)">Translate Debugging Documentation from English to Arabic</a></span>
                    <div class="task-single-content-bottom clearfix">
                        <div class="task-single-content-col1">
                            <span class="task-single-info task-single-project"><a href="javascript:void(0)">Mozilla Project</a></span>
                        </div>
                        <div class="task-single-content-col2">
                            <span class="task-single-info task-single-completed-date">Completed: July 20 2011 5:47GMT</span>
                        </div>
                    </div>
                </div>
            </div>
            <!-- end .task-single -->
        </div>
        <!-- end .block.block-completed-task -->
    </div>
    <!-- end .grid_9.main -->

<?php include '../includes/footer.php'?>