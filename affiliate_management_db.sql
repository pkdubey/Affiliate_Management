-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jul 28, 2025 at 10:54 AM
-- Server version: 9.3.0
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `affiliate_management_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `advertisers_advertiser`
--

CREATE TABLE `advertisers_advertiser` (
  `id` bigint NOT NULL,
  `company_name` varchar(255) NOT NULL,
  `contact_person` varchar(255) DEFAULT NULL,
  `email` varchar(254) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `teams_id` varchar(255) DEFAULT NULL,
  `telegram_id` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `advertisers_advertiser`
--

INSERT INTO `advertisers_advertiser` (`id`, `company_name`, `contact_person`, `email`, `is_active`, `name`, `teams_id`, `telegram_id`) VALUES
(1, 'Rohan Technology', 'Rohan', 'rohan@gmail.com', 1, 'Rohan', NULL, NULL),
(2, 'Rohit Technology', 'Rohit', 'rohit@gmail.com', 1, 'Rohit', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `auth_group`
--

CREATE TABLE `auth_group` (
  `id` int NOT NULL,
  `name` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `auth_group`
--

INSERT INTO `auth_group` (`id`, `name`) VALUES
(1, 'Admin'),
(2, 'Publisher');

-- --------------------------------------------------------

--
-- Table structure for table `auth_group_permissions`
--

CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `auth_group_permissions`
--

INSERT INTO `auth_group_permissions` (`id`, `group_id`, `permission_id`) VALUES
(1, 1, 1),
(2, 1, 2),
(3, 1, 3),
(4, 1, 4),
(5, 1, 5),
(6, 1, 6),
(7, 1, 7),
(8, 1, 8),
(9, 1, 9),
(10, 1, 10),
(11, 1, 11),
(12, 1, 12),
(13, 1, 13),
(14, 1, 14),
(15, 1, 15),
(16, 1, 16),
(17, 1, 17),
(18, 1, 18),
(19, 1, 19),
(20, 1, 20),
(21, 1, 21),
(22, 1, 22),
(23, 1, 23),
(24, 1, 24),
(25, 1, 25),
(26, 1, 26),
(27, 1, 27),
(28, 1, 28),
(29, 1, 29),
(30, 1, 30),
(31, 1, 31),
(32, 1, 32),
(33, 1, 33),
(34, 1, 34),
(35, 1, 35),
(36, 1, 36),
(37, 1, 37),
(38, 1, 38),
(39, 1, 39),
(40, 1, 40),
(41, 1, 41),
(42, 1, 42),
(43, 1, 43),
(44, 1, 44),
(45, 1, 45),
(46, 1, 46),
(47, 1, 47),
(48, 1, 48),
(49, 1, 49),
(50, 1, 50),
(51, 1, 51),
(52, 1, 52),
(53, 1, 53),
(54, 1, 54),
(55, 1, 55),
(56, 1, 56),
(57, 1, 57),
(58, 1, 58),
(59, 1, 59),
(60, 1, 60),
(61, 2, 1),
(62, 2, 2),
(63, 2, 3),
(64, 2, 4),
(65, 2, 5),
(66, 2, 6),
(67, 2, 7),
(68, 2, 8),
(69, 2, 9),
(70, 2, 10),
(71, 2, 11),
(72, 2, 12),
(73, 2, 13),
(74, 2, 14),
(75, 2, 15),
(76, 2, 16),
(77, 2, 17),
(78, 2, 18),
(79, 2, 19),
(80, 2, 20),
(81, 2, 21),
(82, 2, 22),
(83, 2, 23),
(84, 2, 24),
(85, 2, 25),
(86, 2, 26),
(87, 2, 27),
(88, 2, 28),
(89, 2, 29),
(90, 2, 30),
(91, 2, 31),
(92, 2, 32),
(93, 2, 33),
(94, 2, 34),
(95, 2, 35),
(96, 2, 36),
(97, 2, 37),
(98, 2, 38),
(99, 2, 39),
(100, 2, 40),
(101, 2, 41),
(102, 2, 42),
(103, 2, 43),
(104, 2, 44),
(105, 2, 45),
(106, 2, 46),
(107, 2, 47),
(108, 2, 48),
(109, 2, 53),
(110, 2, 54),
(111, 2, 55),
(112, 2, 56),
(113, 2, 57),
(114, 2, 58),
(115, 2, 59),
(116, 2, 60);

-- --------------------------------------------------------

--
-- Table structure for table `auth_permission`
--

CREATE TABLE `auth_permission` (
  `id` int NOT NULL,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add log entry', 1, 'add_logentry'),
(2, 'Can change log entry', 1, 'change_logentry'),
(3, 'Can delete log entry', 1, 'delete_logentry'),
(4, 'Can view log entry', 1, 'view_logentry'),
(5, 'Can add permission', 2, 'add_permission'),
(6, 'Can change permission', 2, 'change_permission'),
(7, 'Can delete permission', 2, 'delete_permission'),
(8, 'Can view permission', 2, 'view_permission'),
(9, 'Can add group', 3, 'add_group'),
(10, 'Can change group', 3, 'change_group'),
(11, 'Can delete group', 3, 'delete_group'),
(12, 'Can view group', 3, 'view_group'),
(13, 'Can add content type', 4, 'add_contenttype'),
(14, 'Can change content type', 4, 'change_contenttype'),
(15, 'Can delete content type', 4, 'delete_contenttype'),
(16, 'Can view content type', 4, 'view_contenttype'),
(17, 'Can add session', 5, 'add_session'),
(18, 'Can change session', 5, 'change_session'),
(19, 'Can delete session', 5, 'delete_session'),
(20, 'Can view session', 5, 'view_session'),
(21, 'Can add advertiser', 6, 'add_advertiser'),
(22, 'Can change advertiser', 6, 'change_advertiser'),
(23, 'Can delete advertiser', 6, 'delete_advertiser'),
(24, 'Can view advertiser', 6, 'view_advertiser'),
(25, 'Can add offer', 7, 'add_offer'),
(26, 'Can change offer', 7, 'change_offer'),
(27, 'Can delete offer', 7, 'delete_offer'),
(28, 'Can view offer', 7, 'view_offer'),
(29, 'Can add publisher', 8, 'add_publisher'),
(30, 'Can change publisher', 8, 'change_publisher'),
(31, 'Can delete publisher', 8, 'delete_publisher'),
(32, 'Can view publisher', 8, 'view_publisher'),
(33, 'Can add wishlist', 9, 'add_wishlist'),
(34, 'Can change wishlist', 9, 'change_wishlist'),
(35, 'Can delete wishlist', 9, 'delete_wishlist'),
(36, 'Can view wishlist', 9, 'view_wishlist'),
(37, 'Can add daily revenue sheet', 10, 'add_dailyrevenuesheet'),
(38, 'Can change daily revenue sheet', 10, 'change_dailyrevenuesheet'),
(39, 'Can delete daily revenue sheet', 10, 'delete_dailyrevenuesheet'),
(40, 'Can view daily revenue sheet', 10, 'view_dailyrevenuesheet'),
(41, 'Can add invoice', 11, 'add_invoice'),
(42, 'Can change invoice', 11, 'change_invoice'),
(43, 'Can delete invoice', 11, 'delete_invoice'),
(44, 'Can view invoice', 11, 'view_invoice'),
(45, 'Can add validation', 12, 'add_validation'),
(46, 'Can change validation', 12, 'change_validation'),
(47, 'Can delete validation', 12, 'delete_validation'),
(48, 'Can view validation', 12, 'view_validation'),
(49, 'Can add user', 13, 'add_user'),
(50, 'Can change user', 13, 'change_user'),
(51, 'Can delete user', 13, 'delete_user'),
(52, 'Can view user', 13, 'view_user'),
(53, 'Can add offer', 14, 'add_offer'),
(54, 'Can change offer', 14, 'change_offer'),
(55, 'Can delete offer', 14, 'delete_offer'),
(56, 'Can view offer', 14, 'view_offer'),
(57, 'Can add Dashboard Snapshot', 15, 'add_dashboardsnapshot'),
(58, 'Can change Dashboard Snapshot', 15, 'change_dashboardsnapshot'),
(59, 'Can delete Dashboard Snapshot', 15, 'delete_dashboardsnapshot'),
(60, 'Can view Dashboard Snapshot', 15, 'view_dashboardsnapshot'),
(61, 'Can add match history', 16, 'add_matchhistory'),
(62, 'Can change match history', 16, 'change_matchhistory'),
(63, 'Can delete match history', 16, 'delete_matchhistory'),
(64, 'Can view match history', 16, 'view_matchhistory'),
(65, 'Can add currency rate', 17, 'add_currencyrate'),
(66, 'Can change currency rate', 17, 'change_currencyrate'),
(67, 'Can delete currency rate', 17, 'delete_currencyrate'),
(68, 'Can view currency rate', 17, 'view_currencyrate');

-- --------------------------------------------------------

--
-- Table structure for table `dashboard_dashboardsnapshot`
--

CREATE TABLE `dashboard_dashboardsnapshot` (
  `id` bigint NOT NULL,
  `date` date NOT NULL,
  `total_advertisers` int UNSIGNED NOT NULL,
  `total_publishers` int UNSIGNED NOT NULL,
  `total_offers` int UNSIGNED NOT NULL,
  `total_invoices` int UNSIGNED NOT NULL,
  `revenue_today` decimal(12,2) NOT NULL,
  `revenue_week` decimal(12,2) NOT NULL,
  `revenue_month` decimal(12,2) NOT NULL,
  `daily_revenue_data` json NOT NULL,
  `daily_profit_data` json NOT NULL,
  `invoice_status_summary` json NOT NULL,
  `created_at` datetime(6) NOT NULL
) ;

-- --------------------------------------------------------

--
-- Table structure for table `django_admin_log`
--

CREATE TABLE `django_admin_log` (
  `id` int NOT NULL,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint UNSIGNED NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL
) ;

--
-- Dumping data for table `django_admin_log`
--

INSERT INTO `django_admin_log` (`id`, `action_time`, `object_id`, `object_repr`, `action_flag`, `change_message`, `content_type_id`, `user_id`) VALUES
(1, '2025-07-15 13:30:13.006428', '1', 'pavan05992@gmail.com', 2, '[{\"changed\": {\"fields\": [\"First name\", \"Last name\", \"Role\"]}}]', 13, 1),
(2, '2025-07-17 06:13:09.567764', '2', 'admin', 1, '[{\"added\": {}}]', 13, 1),
(3, '2025-07-17 06:25:14.490042', '2', 'admin@example.com', 2, '[{\"changed\": {\"fields\": [\"Username\"]}}]', 13, 1),
(4, '2025-07-17 06:25:40.624545', '2', 'admin@example.com', 2, '[{\"changed\": {\"fields\": [\"Password\"]}}]', 13, 1),
(5, '2025-07-20 07:36:24.485074', '3', 'Arsad', 1, '[{\"added\": {}}]', 13, 1),
(6, '2025-07-20 07:36:41.935935', '3', 'arsadali636@gmail.com', 2, '[{\"changed\": {\"fields\": [\"Username\"]}}]', 13, 1),
(7, '2025-07-20 07:37:51.462661', '2', 'publisher@example.com', 2, '[{\"changed\": {\"fields\": [\"Username\", \"First name\", \"Email address\", \"Role\"]}}]', 13, 1),
(8, '2025-07-20 07:38:05.931979', '3', 'arsadali636@gmail.com', 2, '[{\"changed\": {\"fields\": [\"Password\"]}}]', 13, 1),
(9, '2025-07-20 07:54:36.990325', '1', 'Publisher object (1)', 1, '[{\"added\": {}}]', 8, 1),
(10, '2025-07-20 07:54:51.706277', '1', 'Rohan', 1, '[{\"added\": {}}]', 6, 1),
(11, '2025-07-25 12:50:32.184834', '1', 'Admin', 1, '[{\"added\": {}}]', 3, 1),
(12, '2025-07-25 12:50:49.853951', '2', 'Publisher', 1, '[{\"added\": {}}]', 3, 1);

-- --------------------------------------------------------

--
-- Table structure for table `django_content_type`
--

CREATE TABLE `django_content_type` (
  `id` int NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(1, 'admin', 'logentry'),
(6, 'advertisers', 'advertiser'),
(7, 'advertisers', 'offer'),
(3, 'auth', 'group'),
(2, 'auth', 'permission'),
(4, 'contenttypes', 'contenttype'),
(15, 'dashboard', 'dashboardsnapshot'),
(10, 'drs', 'dailyrevenuesheet'),
(17, 'invoicing', 'currencyrate'),
(11, 'invoicing', 'invoice'),
(16, 'offers', 'matchhistory'),
(14, 'offers', 'offer'),
(8, 'publishers', 'publisher'),
(9, 'publishers', 'wishlist'),
(5, 'sessions', 'session'),
(13, 'users', 'user'),
(12, 'validation', 'validation');

-- --------------------------------------------------------

--
-- Table structure for table `django_migrations`
--

CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2025-07-15 12:35:28.114119'),
(2, 'contenttypes', '0002_remove_content_type_name', '2025-07-15 12:35:28.270287'),
(3, 'auth', '0001_initial', '2025-07-15 12:35:28.767351'),
(4, 'auth', '0002_alter_permission_name_max_length', '2025-07-15 12:35:28.900640'),
(5, 'auth', '0003_alter_user_email_max_length', '2025-07-15 12:35:28.910386'),
(6, 'auth', '0004_alter_user_username_opts', '2025-07-15 12:35:28.920936'),
(7, 'auth', '0005_alter_user_last_login_null', '2025-07-15 12:35:28.934095'),
(8, 'auth', '0006_require_contenttypes_0002', '2025-07-15 12:35:28.939361'),
(9, 'auth', '0007_alter_validators_add_error_messages', '2025-07-15 12:35:28.948070'),
(10, 'auth', '0008_alter_user_username_max_length', '2025-07-15 12:35:28.958944'),
(11, 'auth', '0009_alter_user_last_name_max_length', '2025-07-15 12:35:28.968220'),
(12, 'auth', '0010_alter_group_name_max_length', '2025-07-15 12:35:28.992929'),
(13, 'auth', '0011_update_proxy_permissions', '2025-07-15 12:35:29.005431'),
(14, 'auth', '0012_alter_user_first_name_max_length', '2025-07-15 12:35:29.016190'),
(15, 'users', '0001_initial', '2025-07-15 12:35:29.570690'),
(16, 'admin', '0001_initial', '2025-07-15 12:35:29.767702'),
(17, 'admin', '0002_logentry_remove_auto_add', '2025-07-15 12:35:29.781319'),
(18, 'admin', '0003_logentry_add_action_flag_choices', '2025-07-15 12:35:29.797677'),
(19, 'advertisers', '0001_initial', '2025-07-15 12:35:29.915079'),
(20, 'publishers', '0001_initial', '2025-07-15 12:35:30.065023'),
(21, 'drs', '0001_initial', '2025-07-15 12:35:30.277428'),
(22, 'invoicing', '0001_initial', '2025-07-15 12:35:30.471444'),
(23, 'sessions', '0001_initial', '2025-07-15 12:35:30.530537'),
(24, 'validation', '0001_initial', '2025-07-15 12:35:30.787772'),
(25, 'advertisers', '0002_delete_offer', '2025-07-16 09:50:20.431475'),
(26, 'offers', '0001_initial', '2025-07-16 09:50:20.600077'),
(27, 'dashboard', '0001_initial', '2025-07-16 09:53:14.818181'),
(28, 'advertisers', '0003_rename_name_advertiser_company_name_and_more', '2025-07-22 11:14:52.390673'),
(29, 'publishers', '0002_rename_name_publisher_company_name_and_more', '2025-07-22 11:31:09.701183'),
(30, 'advertisers', '0004_advertiser_name_advertiser_teams_id_and_more', '2025-07-26 02:14:12.811344'),
(31, 'offers', '0002_offer_mmp_offer_model_offer_payable_event_and_more', '2025-07-26 02:14:13.067186'),
(32, 'publishers', '0003_publisher_name_publisher_teams_id_and_more', '2025-07-26 02:32:56.972661'),
(33, 'offers', '0003_alter_offer_payout_matchhistory', '2025-07-26 03:30:19.330731'),
(34, 'drs', '0002_dailyrevenuesheet_updated_at_and_more', '2025-07-26 12:03:01.161212'),
(35, 'validation', '0002_validation_approve_payout_validation_conversions_and_more', '2025-07-26 13:02:13.378864'),
(36, 'invoicing', '0002_invoice_amount_invoice_currency_invoice_gst_amount_and_more', '2025-07-27 02:19:49.268867'),
(37, 'invoicing', '0003_currencyrate', '2025-07-27 03:03:40.519732'),
(38, 'publishers', '0004_wishlist_created_at_wishlist_updated_at', '2025-07-28 08:34:03.669019');

-- --------------------------------------------------------

--
-- Table structure for table `django_session`
--

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `django_session`
--

INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
('ccu83xhvic0744oh5ofh6yfdm8x1bpsc', '.eJxVjEEOwiAQRe_C2pAOIBCX7j0DGZgZqRqalHbVeHdt0oVu_3vvbyrhutS0dp7TSOqiQJ1-t4zlyW0H9MB2n3SZ2jKPWe-KPmjXt4n4dT3cv4OKvX5rL4GtQ7JnAPBAjq2JRkIRpiKQM2crEgaXyReOYIWAPdkBY2Q0pN4f_2k5Fw:1ufUsV:UqLPTAdfUpSwm1GFEiq_nzVn2R4Nm3dQwtBmMjj810E', '2025-08-09 02:43:15.848945'),
('e1uvlp5v3o648wryyv55wvvy2eui53n9', '.eJxVjEEOwiAQRe_C2pAOIBCX7j0DGZgZqRqalHbVeHdt0oVu_3vvbyrhutS0dp7TSOqiQJ1-t4zlyW0H9MB2n3SZ2jKPWe-KPmjXt4n4dT3cv4OKvX5rL4GtQ7JnAPBAjq2JRkIRpiKQM2crEgaXyReOYIWAPdkBY2Q0pN4f_2k5Fw:1udDqv:6BgHOzzvekMHz6-PZu-fUp0tvVyyuHFZ888-fn4y0wU', '2025-08-02 20:08:13.114849'),
('q9okkjhllvl4fvd0in1gc0lspgvigbhq', '.eJxVjEEOwiAQRe_C2pAOIBCX7j0DGZgZqRqalHbVeHdt0oVu_3vvbyrhutS0dp7TSOqiQJ1-t4zlyW0H9MB2n3SZ2jKPWe-KPmjXt4n4dT3cv4OKvX5rL4GtQ7JnAPBAjq2JRkIRpiKQM2crEgaXyReOYIWAPdkBY2Q0pN4f_2k5Fw:1udM4A:RvOKJvyKI7B1aUWys9e3nf3v4oaoqETedWOmn2vapNk', '2025-08-03 04:54:26.937467'),
('xhfb0ul0t9qf16byhy404y3fwt0b8a6v', '.eJxVjEEOwiAQRe_C2pAOIBCX7j0DGZgZqRqalHbVeHdt0oVu_3vvbyrhutS0dp7TSOqiQJ1-t4zlyW0H9MB2n3SZ2jKPWe-KPmjXt4n4dT3cv4OKvX5rL4GtQ7JnAPBAjq2JRkIRpiKQM2crEgaXyReOYIWAPdkBY2Q0pN4f_2k5Fw:1udLyh:Dtal83jPM77DxezziE4Ce5CqX_ZVIzmwXM0JfBoeyQM', '2025-08-03 04:48:47.357676');

-- --------------------------------------------------------

--
-- Table structure for table `drs_dailyrevenuesheet`
--

CREATE TABLE `drs_dailyrevenuesheet` (
  `id` bigint NOT NULL,
  `campaign_name` varchar(255) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `advertiser_conversions` int NOT NULL,
  `publisher_conversions` int NOT NULL,
  `campaign_revenue` decimal(12,2) NOT NULL,
  `publisher_payout` decimal(12,2) NOT NULL,
  `revenue` decimal(12,2) DEFAULT NULL,
  `payout` decimal(12,2) DEFAULT NULL,
  `profit` decimal(12,2) DEFAULT NULL,
  `pid` varchar(100) NOT NULL,
  `af_prt` varchar(100) NOT NULL,
  `account_manager` varchar(100) NOT NULL,
  `advertiser_id` bigint NOT NULL,
  `affiliate_id` bigint NOT NULL,
  `updated_at` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `drs_dailyrevenuesheet`
--

INSERT INTO `drs_dailyrevenuesheet` (`id`, `campaign_name`, `start_date`, `end_date`, `advertiser_conversions`, `publisher_conversions`, `campaign_revenue`, `publisher_payout`, `revenue`, `payout`, `profit`, `pid`, `af_prt`, `account_manager`, `advertiser_id`, `affiliate_id`, `updated_at`) VALUES
(1, 'Uber India', '2025-07-26', '2025-07-26', 100, 90, 2.30, 1.60, 230.00, 144.00, 86.00, 'PUB12345', 'prt_98765', 'John Smith', 1, 1, '2025-07-26 12:17:25.322893');

-- --------------------------------------------------------

--
-- Table structure for table `invoicing_currencyrate`
--

CREATE TABLE `invoicing_currencyrate` (
  `id` bigint NOT NULL,
  `currency` varchar(3) NOT NULL,
  `rate_to_inr` decimal(12,6) NOT NULL,
  `last_updated` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `invoicing_currencyrate`
--

INSERT INTO `invoicing_currencyrate` (`id`, `currency`, `rate_to_inr`, `last_updated`) VALUES
(1, 'USD', 0.012000, '2025-07-27'),
(2, 'EUR', 0.011000, '2025-07-27');

-- --------------------------------------------------------

--
-- Table structure for table `invoicing_invoice`
--

CREATE TABLE `invoicing_invoice` (
  `id` bigint NOT NULL,
  `status` varchar(20) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `drs_id` bigint NOT NULL,
  `publisher_id` bigint NOT NULL,
  `amount` decimal(12,2) NOT NULL,
  `currency` varchar(3) NOT NULL,
  `gst_amount` decimal(12,2) NOT NULL,
  `pdf` varchar(100) DEFAULT NULL,
  `publisher_upload` varchar(100) DEFAULT NULL,
  `total_amount` decimal(12,2) NOT NULL,
  `updated_at` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `invoicing_invoice`
--

INSERT INTO `invoicing_invoice` (`id`, `status`, `created_at`, `drs_id`, `publisher_id`, `amount`, `currency`, `gst_amount`, `pdf`, `publisher_upload`, `total_amount`, `updated_at`) VALUES
(1, 'Pending', '2025-07-27 03:22:36.616674', 1, 1, 144.00, 'INR', 25.92, '', '', 169.92, '2025-07-27 04:56:01.379856');

-- --------------------------------------------------------

--
-- Table structure for table `offers_matchhistory`
--

CREATE TABLE `offers_matchhistory` (
  `id` bigint NOT NULL,
  `matched_at` datetime(6) NOT NULL,
  `offer_id` bigint NOT NULL,
  `wishlist_id` bigint NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `offers_matchhistory`
--

INSERT INTO `offers_matchhistory` (`id`, `matched_at`, `offer_id`, `wishlist_id`) VALUES
(1, '2025-07-26 03:30:36.471735', 1, 1);

-- --------------------------------------------------------

--
-- Table structure for table `offers_offer`
--

CREATE TABLE `offers_offer` (
  `id` bigint NOT NULL,
  `campaign_name` varchar(255) NOT NULL,
  `geo` varchar(100) NOT NULL,
  `category` varchar(100) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` longtext,
  `payout` decimal(10,2) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `advertiser_id` bigint NOT NULL,
  `mmp` varchar(128) DEFAULT NULL,
  `model` varchar(255) DEFAULT NULL,
  `payable_event` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `offers_offer`
--

INSERT INTO `offers_offer` (`id`, `campaign_name`, `geo`, `category`, `title`, `description`, `payout`, `is_active`, `created_at`, `updated_at`, `advertiser_id`, `mmp`, `model`, `payable_event`) VALUES
(1, 'Uber India', 'IN', 'Transport', 'Uber India', NULL, 2.50, 1, '2025-07-26 02:56:20.053383', '2025-07-26 02:56:20.053511', 1, 'Adjust', 'CPI', 'Install'),
(2, 'Swiggy Food App', 'IN', 'Food', 'Swiggy Food App', NULL, 1.70, 1, '2025-07-26 02:58:26.015264', '2025-07-26 02:58:26.015309', 2, 'AppsFlyer', 'CPI', 'Install'),
(3, 'Fashion US', 'US', 'Fashion', 'Fashion US', NULL, 3.00, 1, '2025-07-26 02:59:17.820438', '2025-07-26 02:59:17.820488', 1, 'Branch', 'Signup', 'Signup');

-- --------------------------------------------------------

--
-- Table structure for table `publishers_publisher`
--

CREATE TABLE `publishers_publisher` (
  `id` bigint NOT NULL,
  `company_name` varchar(255) NOT NULL,
  `contact_person` varchar(255) DEFAULT NULL,
  `email` varchar(254) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `teams_id` varchar(255) DEFAULT NULL,
  `telegram_id` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `publishers_publisher`
--

INSERT INTO `publishers_publisher` (`id`, `company_name`, `contact_person`, `email`, `is_active`, `name`, `teams_id`, `telegram_id`) VALUES
(1, 'Arsad Technology', 'Arsad', 'arsad@gmail.com', 1, 'Arsad', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `publishers_wishlist`
--

CREATE TABLE `publishers_wishlist` (
  `id` bigint NOT NULL,
  `desired_campaign` varchar(255) NOT NULL,
  `geo` varchar(100) NOT NULL,
  `category` varchar(100) DEFAULT NULL,
  `publisher_id` bigint NOT NULL,
  `model` varchar(255) DEFAULT NULL,
  `payable_event` varchar(255) DEFAULT NULL,
  `payout` decimal(10,2) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `publishers_wishlist`
--

INSERT INTO `publishers_wishlist` (`id`, `desired_campaign`, `geo`, `category`, `publisher_id`, `model`, `payable_event`, `payout`, `created_at`, `updated_at`) VALUES
(1, 'Uber India', 'IN', 'Transport', 1, 'CPI', 'Install', 1.50, '2025-07-28 08:33:50.258824', '2025-07-28 08:34:03.608019'),
(2, 'Zara US', 'US', 'Fashion', 1, 'CPS', 'Purchase', 2.50, '2025-07-28 08:33:50.258824', '2025-07-28 08:34:03.608019'),
(3, 'Flipkart IN', 'IN', 'Shopping', 1, 'CPS', 'Registration', 2.00, '2025-07-28 08:33:50.258824', '2025-07-28 08:34:03.608019');

-- --------------------------------------------------------

--
-- Table structure for table `users_user`
--

CREATE TABLE `users_user` (
  `id` bigint NOT NULL,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `role` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `users_user`
--

INSERT INTO `users_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`, `role`) VALUES
(1, 'pbkdf2_sha256$1000000$O7FHrw82Zn4hXr2Qp9ddY5$w85tShSyKlChNGv/I7ZXaSEUStWtIJDVDmSXrTJQNiE=', '2025-07-26 02:43:15.843820', 1, 'pavan05992@gmail.com', 'Pavan', 'Dubey', 'pavan05992@gmail.com', 1, 1, '2025-07-15 13:28:46.000000', 'admin'),
(2, 'pbkdf2_sha256$1000000$O7FHrw82Zn4hXr2Qp9ddY5$w85tShSyKlChNGv/I7ZXaSEUStWtIJDVDmSXrTJQNiE=', '2025-07-20 08:15:16.325604', 0, 'publisher@example.com', 'publisher', 'User', 'publisher@example.com', 1, 1, '2025-07-17 06:11:11.000000', 'publisher'),
(3, 'pbkdf2_sha256$1000000$O7FHrw82Zn4hXr2Qp9ddY5$w85tShSyKlChNGv/I7ZXaSEUStWtIJDVDmSXrTJQNiE=', NULL, 0, 'arsadali636@gmail.com', 'Arsad', 'Ali', 'arsadali636@gmail.com', 1, 1, '2025-07-20 07:35:41.000000', 'admin');

-- --------------------------------------------------------

--
-- Table structure for table `users_user_groups`
--

CREATE TABLE `users_user_groups` (
  `id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `group_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `users_user_groups`
--

INSERT INTO `users_user_groups` (`id`, `user_id`, `group_id`) VALUES
(1, 1, 1),
(2, 2, 2),
(3, 3, 1);

-- --------------------------------------------------------

--
-- Table structure for table `users_user_user_permissions`
--

CREATE TABLE `users_user_user_permissions` (
  `id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `permission_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `users_user_user_permissions`
--

INSERT INTO `users_user_user_permissions` (`id`, `user_id`, `permission_id`) VALUES
(1, 2, 1),
(2, 2, 2),
(3, 2, 3),
(4, 2, 4),
(5, 2, 5),
(6, 2, 6),
(7, 2, 7),
(8, 2, 8),
(9, 2, 9),
(10, 2, 10),
(11, 2, 11),
(12, 2, 12),
(13, 2, 13),
(14, 2, 14),
(15, 2, 15),
(16, 2, 16),
(17, 2, 17),
(18, 2, 18),
(19, 2, 19),
(20, 2, 20),
(21, 2, 21),
(22, 2, 22),
(23, 2, 23),
(24, 2, 24),
(25, 2, 25),
(26, 2, 26),
(27, 2, 27),
(28, 2, 28),
(29, 2, 29),
(30, 2, 30),
(31, 2, 31),
(32, 2, 32),
(33, 2, 33),
(34, 2, 34),
(35, 2, 35),
(36, 2, 36),
(37, 2, 37),
(38, 2, 38),
(39, 2, 39),
(40, 2, 40),
(41, 2, 41),
(42, 2, 42),
(43, 2, 43),
(44, 2, 44),
(45, 2, 45),
(46, 2, 46),
(47, 2, 47),
(48, 2, 48),
(49, 2, 49),
(50, 2, 50),
(51, 2, 51),
(52, 2, 52),
(53, 2, 53),
(54, 2, 54),
(55, 2, 55),
(56, 2, 56),
(57, 2, 57),
(58, 2, 58),
(59, 2, 59),
(60, 2, 60);

-- --------------------------------------------------------

--
-- Table structure for table `validation_validation`
--

CREATE TABLE `validation_validation` (
  `id` bigint NOT NULL,
  `month` varchar(20) NOT NULL,
  `status` varchar(20) NOT NULL,
  `drs_id` bigint NOT NULL,
  `publisher_id` bigint NOT NULL,
  `approve_payout` decimal(12,2) NOT NULL,
  `conversions` int NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `payout` decimal(12,2) NOT NULL,
  `updated_at` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `validation_validation`
--

INSERT INTO `validation_validation` (`id`, `month`, `status`, `drs_id`, `publisher_id`, `approve_payout`, `conversions`, `created_at`, `payout`, `updated_at`) VALUES
(1, '2025-07', 'Approved', 1, 1, 1.60, 90, '2025-07-26 14:15:21.913787', 1.60, '2025-07-26 15:33:08.106861');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `advertisers_advertiser`
--
ALTER TABLE `advertisers_advertiser`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `auth_group`
--
ALTER TABLE `auth_group`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  ADD KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`);

--
-- Indexes for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`);

--
-- Indexes for table `dashboard_dashboardsnapshot`
--
ALTER TABLE `dashboard_dashboardsnapshot`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `date` (`date`);

--
-- Indexes for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  ADD KEY `django_admin_log_user_id_c564eba6_fk_users_user_id` (`user_id`);

--
-- Indexes for table `django_content_type`
--
ALTER TABLE `django_content_type`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`);

--
-- Indexes for table `django_migrations`
--
ALTER TABLE `django_migrations`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `django_session`
--
ALTER TABLE `django_session`
  ADD PRIMARY KEY (`session_key`),
  ADD KEY `django_session_expire_date_a5c62663` (`expire_date`);

--
-- Indexes for table `drs_dailyrevenuesheet`
--
ALTER TABLE `drs_dailyrevenuesheet`
  ADD PRIMARY KEY (`id`),
  ADD KEY `drs_dailyrevenueshee_advertiser_id_a06d5b53_fk_advertise` (`advertiser_id`),
  ADD KEY `drs_dailyrevenueshee_affiliate_id_c1e480a0_fk_publisher` (`affiliate_id`);

--
-- Indexes for table `invoicing_currencyrate`
--
ALTER TABLE `invoicing_currencyrate`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `currency` (`currency`);

--
-- Indexes for table `invoicing_invoice`
--
ALTER TABLE `invoicing_invoice`
  ADD PRIMARY KEY (`id`),
  ADD KEY `invoicing_invoice_drs_id_36ca7614_fk_drs_dailyrevenuesheet_id` (`drs_id`),
  ADD KEY `invoicing_invoice_publisher_id_141079a0_fk_publisher` (`publisher_id`);

--
-- Indexes for table `offers_matchhistory`
--
ALTER TABLE `offers_matchhistory`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `offers_matchhistory_offer_id_wishlist_id_6744b64a_uniq` (`offer_id`,`wishlist_id`),
  ADD KEY `offers_matchhistory_wishlist_id_6b714a65_fk_publisher` (`wishlist_id`);

--
-- Indexes for table `offers_offer`
--
ALTER TABLE `offers_offer`
  ADD PRIMARY KEY (`id`),
  ADD KEY `offers_offer_advertiser_id_860746cf_fk_advertisers_advertiser_id` (`advertiser_id`);

--
-- Indexes for table `publishers_publisher`
--
ALTER TABLE `publishers_publisher`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `publishers_wishlist`
--
ALTER TABLE `publishers_wishlist`
  ADD PRIMARY KEY (`id`),
  ADD KEY `publishers_wishlist_publisher_id_0fa8050e_fk_publisher` (`publisher_id`);

--
-- Indexes for table `users_user`
--
ALTER TABLE `users_user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `users_user_groups`
--
ALTER TABLE `users_user_groups`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `users_user_groups_user_id_group_id_b88eab82_uniq` (`user_id`,`group_id`),
  ADD KEY `users_user_groups_group_id_9afc8d0e_fk_auth_group_id` (`group_id`);

--
-- Indexes for table `users_user_user_permissions`
--
ALTER TABLE `users_user_user_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `users_user_user_permissions_user_id_permission_id_43338c45_uniq` (`user_id`,`permission_id`),
  ADD KEY `users_user_user_perm_permission_id_0b93982e_fk_auth_perm` (`permission_id`);

--
-- Indexes for table `validation_validation`
--
ALTER TABLE `validation_validation`
  ADD PRIMARY KEY (`id`),
  ADD KEY `validation_validatio_drs_id_8c50246b_fk_drs_daily` (`drs_id`),
  ADD KEY `validation_validatio_publisher_id_e6f1d0b8_fk_publisher` (`publisher_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `advertisers_advertiser`
--
ALTER TABLE `advertisers_advertiser`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `auth_group`
--
ALTER TABLE `auth_group`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=117;

--
-- AUTO_INCREMENT for table `auth_permission`
--
ALTER TABLE `auth_permission`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=69;

--
-- AUTO_INCREMENT for table `dashboard_dashboardsnapshot`
--
ALTER TABLE `dashboard_dashboardsnapshot`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `django_content_type`
--
ALTER TABLE `django_content_type`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT for table `django_migrations`
--
ALTER TABLE `django_migrations`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=39;

--
-- AUTO_INCREMENT for table `drs_dailyrevenuesheet`
--
ALTER TABLE `drs_dailyrevenuesheet`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `invoicing_currencyrate`
--
ALTER TABLE `invoicing_currencyrate`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `invoicing_invoice`
--
ALTER TABLE `invoicing_invoice`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `offers_matchhistory`
--
ALTER TABLE `offers_matchhistory`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `offers_offer`
--
ALTER TABLE `offers_offer`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `publishers_publisher`
--
ALTER TABLE `publishers_publisher`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `publishers_wishlist`
--
ALTER TABLE `publishers_wishlist`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `users_user`
--
ALTER TABLE `users_user`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `users_user_groups`
--
ALTER TABLE `users_user_groups`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `users_user_user_permissions`
--
ALTER TABLE `users_user_user_permissions`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=61;

--
-- AUTO_INCREMENT for table `validation_validation`
--
ALTER TABLE `validation_validation`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Constraints for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);

--
-- Constraints for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  ADD CONSTRAINT `django_admin_log_user_id_c564eba6_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`);

--
-- Constraints for table `drs_dailyrevenuesheet`
--
ALTER TABLE `drs_dailyrevenuesheet`
  ADD CONSTRAINT `drs_dailyrevenueshee_advertiser_id_a06d5b53_fk_advertise` FOREIGN KEY (`advertiser_id`) REFERENCES `advertisers_advertiser` (`id`),
  ADD CONSTRAINT `drs_dailyrevenueshee_affiliate_id_c1e480a0_fk_publisher` FOREIGN KEY (`affiliate_id`) REFERENCES `publishers_publisher` (`id`);

--
-- Constraints for table `invoicing_invoice`
--
ALTER TABLE `invoicing_invoice`
  ADD CONSTRAINT `invoicing_invoice_drs_id_36ca7614_fk_drs_dailyrevenuesheet_id` FOREIGN KEY (`drs_id`) REFERENCES `drs_dailyrevenuesheet` (`id`),
  ADD CONSTRAINT `invoicing_invoice_publisher_id_141079a0_fk_publisher` FOREIGN KEY (`publisher_id`) REFERENCES `publishers_publisher` (`id`);

--
-- Constraints for table `offers_matchhistory`
--
ALTER TABLE `offers_matchhistory`
  ADD CONSTRAINT `offers_matchhistory_offer_id_c5e7d755_fk_offers_offer_id` FOREIGN KEY (`offer_id`) REFERENCES `offers_offer` (`id`),
  ADD CONSTRAINT `offers_matchhistory_wishlist_id_6b714a65_fk_publisher` FOREIGN KEY (`wishlist_id`) REFERENCES `publishers_wishlist` (`id`);

--
-- Constraints for table `offers_offer`
--
ALTER TABLE `offers_offer`
  ADD CONSTRAINT `offers_offer_advertiser_id_860746cf_fk_advertisers_advertiser_id` FOREIGN KEY (`advertiser_id`) REFERENCES `advertisers_advertiser` (`id`);

--
-- Constraints for table `publishers_wishlist`
--
ALTER TABLE `publishers_wishlist`
  ADD CONSTRAINT `publishers_wishlist_publisher_id_0fa8050e_fk_publisher` FOREIGN KEY (`publisher_id`) REFERENCES `publishers_publisher` (`id`);

--
-- Constraints for table `users_user_groups`
--
ALTER TABLE `users_user_groups`
  ADD CONSTRAINT `users_user_groups_group_id_9afc8d0e_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  ADD CONSTRAINT `users_user_groups_user_id_5f6f5a90_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`);

--
-- Constraints for table `users_user_user_permissions`
--
ALTER TABLE `users_user_user_permissions`
  ADD CONSTRAINT `users_user_user_perm_permission_id_0b93982e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `users_user_user_permissions_user_id_20aca447_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`);

--
-- Constraints for table `validation_validation`
--
ALTER TABLE `validation_validation`
  ADD CONSTRAINT `validation_validatio_drs_id_8c50246b_fk_drs_daily` FOREIGN KEY (`drs_id`) REFERENCES `drs_dailyrevenuesheet` (`id`),
  ADD CONSTRAINT `validation_validatio_publisher_id_e6f1d0b8_fk_publisher` FOREIGN KEY (`publisher_id`) REFERENCES `publishers_publisher` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
